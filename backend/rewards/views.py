"""
Views for the rewards app.
Provides endpoints for badges, XP, streaks, leaderboards, and credits.
"""
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Sum, Count, F
from django.contrib.auth import get_user_model

from .models import (
    Reward, UserReward, Achievement, UserAchievement, 
    RewardEvent, Streak, CreditWallet, CreditTransaction, CreditConfig
)
from .serializers import (
    RewardSerializer, UserRewardSerializer, BadgeSerializer,
    AchievementSerializer, UserAchievementSerializer,
    RewardEventSerializer, StreakSerializer, UserProgressSerializer,
    LeaderboardEntrySerializer,
    CreditWalletSerializer, CreditTransactionSerializer, CreditConfigSerializer,
    CreditBalanceSerializer, ChallengeCostSerializer, ChallengeCostResponseSerializer,
    AdminCreditActionSerializer, EconomyStatsSerializer
)
from .services import CreditService

User = get_user_model()


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing available badges.
    Users can see all badges (to know what to work towards).
    """
    queryset = Reward.objects.filter(reward_type='badge', is_available=True)
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def earned(self, request):
        """Get badges earned by the current user."""
        user_rewards = UserReward.objects.filter(
            user=request.user,
            reward__reward_type='badge'
        ).select_related('reward')
        serializer = UserRewardSerializer(user_rewards, many=True)
        return Response(serializer.data)


class RewardEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing reward events (XP/coins earned).
    Users can only see their own reward history.
    """
    serializer_class = RewardEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RewardEvent.objects.filter(
            user=self.request.user
        ).select_related('user').order_by('-created_at')


class StreakViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user streaks.
    Users can only see their own streaks.
    """
    serializer_class = StreakSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Streak.objects.filter(user=self.request.user)


class UserProgressView(APIView):
    """
    Get aggregated progress for the current user.
    Includes XP, level, coins, active streaks, badges.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get streak info
        streaks = Streak.objects.filter(user=user)
        active_streaks = streaks.filter(current_count__gt=0)
        best_streak = streaks.order_by('-best_count').first()
        
        # Get badge count
        badge_count = UserReward.objects.filter(
            user=user,
            reward__reward_type='badge'
        ).count()
        
        # Get recent rewards
        recent_events = RewardEvent.objects.filter(user=user)[:10]
        
        # Calculate weekly XP
        from django.utils import timezone
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        weekly_xp = RewardEvent.objects.filter(
            user=user,
            created_at__gte=week_ago
        ).aggregate(total=Sum('xp_amount'))['total'] or 0
        
        data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'avatar': user.avatar.url if user.avatar else None,
            },
            'xp': {
                'total': user.total_points,
                'level': user.level,
                'weekly': weekly_xp,
                'to_next_level': ((user.level) * 100) - (user.total_points % 100),
            },
            'streaks': {
                'active_count': active_streaks.count(),
                'best_ever': best_streak.best_count if best_streak else 0,
                'current_best': active_streaks.order_by('-current_count').first().current_count if active_streaks.exists() else 0,
            },
            'badges': {
                'total': badge_count,
            },
            'recent_rewards': RewardEventSerializer(recent_events, many=True).data,
        }
        
        return Response(data)


class LeaderboardView(APIView):
    """
    Get leaderboard data.
    Supports: global, friends, team leaderboards.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        leaderboard_type = request.query_params.get('type', 'global')
        limit = min(int(request.query_params.get('limit', 50)), 100)
        
        if leaderboard_type == 'global':
            users = User.objects.filter(
                is_active=True
            ).order_by('-total_points')[:limit]
        elif leaderboard_type == 'weekly':
            from django.utils import timezone
            from datetime import timedelta
            week_ago = timezone.now() - timedelta(days=7)
            
            users = User.objects.filter(
                is_active=True,
                reward_events__created_at__gte=week_ago
            ).annotate(
                weekly_xp=Sum('reward_events__xp_amount')
            ).order_by('-weekly_xp')[:limit]
        else:
            users = User.objects.filter(is_active=True).order_by('-total_points')[:limit]
        
        # Add rank to results
        results = []
        for i, user in enumerate(users, 1):
            results.append({
                'rank': i,
                'user_id': user.id,
                'username': user.username,
                'avatar': user.avatar.url if user.avatar else None,
                'total_points': user.total_points,
                'level': user.level,
            })
        
        # Find current user's rank
        current_user_rank = None
        try:
            users_above = User.objects.filter(
                total_points__gt=request.user.total_points
            ).count()
            current_user_rank = users_above + 1
        except Exception:
            pass
        
        return Response({
            'type': leaderboard_type,
            'entries': results,
            'current_user_rank': current_user_rank,
        })


# ============================================
# Credit Economy Views
# ============================================

class CreditWalletView(APIView):
    """
    Get current user's credit wallet.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        wallet, created = CreditService.get_or_create_wallet(request.user)
        
        # If newly created, grant signup bonus
        if created:
            CreditService.grant_signup_bonus(request.user)
            wallet.refresh_from_db()
        
        serializer = CreditWalletSerializer(wallet)
        return Response(serializer.data)


class CreditBalanceView(APIView):
    """
    Quick balance check endpoint.
    Optionally check if user can afford a specific amount.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        balance = CreditService.get_balance(request.user)
        check_amount = request.query_params.get('check_amount')
        
        data = {'balance': balance}
        
        if check_amount:
            try:
                amount = int(check_amount)
                data['can_afford'] = balance >= amount
            except ValueError:
                pass
        
        return Response(data)


class CreditTransactionListView(generics.ListAPIView):
    """
    List user's credit transactions with pagination.
    """
    serializer_class = CreditTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        wallet, _ = CreditService.get_or_create_wallet(self.request.user)
        queryset = CreditTransaction.objects.filter(wallet=wallet)
        
        # Filter by type
        tx_type = self.request.query_params.get('type')
        if tx_type:
            queryset = queryset.filter(transaction_type=tx_type)
        
        # Filter by direction (earning/spending)
        direction = self.request.query_params.get('direction')
        if direction == 'earning':
            queryset = queryset.filter(amount__gt=0)
        elif direction == 'spending':
            queryset = queryset.filter(amount__lt=0)
        
        return queryset.order_by('-created_at')


class ChallengeCostView(APIView):
    """
    Calculate the credit cost for creating a challenge.
    Helps users understand costs before committing.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChallengeCostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        challenge_type = serializer.validated_data['challenge_type']
        proof_type = serializer.validated_data.get('proof_type')
        
        config = CreditConfig.get_config()
        balance = CreditService.get_balance(request.user)
        
        # Calculate costs
        cost_map = {
            'todo': config.cost_todo,
            'streak': config.cost_streak,
            'quantified': config.cost_quantified,
            'duel': config.cost_duel,
            'team': config.cost_team,
            'community': config.cost_community,
        }
        base_cost = cost_map.get(challenge_type, config.cost_todo)
        
        proof_cost = 0
        if proof_type == 'PHOTO':
            proof_cost = config.cost_photo_proof
        elif proof_type == 'VIDEO':
            proof_cost = config.cost_video_proof
        elif proof_type == 'PEER':
            proof_cost = config.cost_peer_review
        
        total_cost = base_cost + proof_cost
        
        return Response({
            'base_cost': base_cost,
            'proof_cost': proof_cost,
            'total_cost': total_cost,
            'can_afford': balance >= total_cost,
            'current_balance': balance,
        })


class CreditConfigView(APIView):
    """
    Get the current credit economy configuration.
    Allows clients to display costs without hardcoding.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        config = CreditConfig.get_config()
        serializer = CreditConfigSerializer(config)
        return Response(serializer.data)


class CreditPurchaseView(APIView):
    """
    Endpoint for users to "purchase" credits.
    In demo mode, this grants credits directly.
    In production, this would integrate with a payment provider.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        amount = request.data.get('amount')
        reason = request.data.get('reason', 'Credit-Kauf')
        
        if not amount or not isinstance(amount, int) or amount < 1:
            return Response(
                {'error': 'Ungültiger Betrag'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount > 10000:
            return Response(
                {'error': 'Maximaler Kaufbetrag: 10.000 Credits'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # In demo mode, grant credits directly
            # In production, this would be triggered after payment confirmation
            transaction = CreditService.admin_grant(
                user=request.user,
                amount=amount,
                reason=f"[Demo] {reason}",
                admin_user=None  # Self-purchase
            )
            
            wallet = CreditService.get_wallet_details(request.user)
            
            return Response({
                'success': True,
                'amount': amount,
                'new_balance': wallet['balance'],
                'transaction': CreditTransactionSerializer(transaction).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AdminCreditGrantView(APIView):
    """
    Admin endpoint to grant credits to a user.
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        serializer = AdminCreditActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(id=serializer.validated_data['user_id'])
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            transaction = CreditService.admin_grant(
                user=user,
                amount=serializer.validated_data['amount'],
                reason=serializer.validated_data['reason'],
                admin_user=request.user
            )
            return Response({
                'success': True,
                'transaction': CreditTransactionSerializer(transaction).data
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AdminCreditDeductView(APIView):
    """
    Admin endpoint to deduct credits from a user.
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        serializer = AdminCreditActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(id=serializer.validated_data['user_id'])
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            transaction = CreditService.admin_deduct(
                user=user,
                amount=serializer.validated_data['amount'],
                reason=serializer.validated_data['reason'],
                admin_user=request.user
            )
            return Response({
                'success': True,
                'transaction': CreditTransactionSerializer(transaction).data
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class EconomyStatsView(APIView):
    """
    Admin endpoint to view economy-wide statistics.
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        stats = CreditService.get_economy_stats()
        serializer = EconomyStatsSerializer(stats)
        return Response(serializer.data)
