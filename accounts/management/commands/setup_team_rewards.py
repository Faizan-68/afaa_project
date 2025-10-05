# accounts/management/commands/setup_team_rewards.py
from django.core.management.base import BaseCommand
from accounts.models import TeamReward

class Command(BaseCommand):
    help = 'Setup predefined team rewards for Afaa Elevate'

    def handle(self, *args, **options):
        # Clear existing rewards first
        TeamReward.objects.all().delete()
        
        # Define the team rewards as specified
        rewards_data = [
            {
                'referrals_required': 10,
                'reward_name': 'Watch',
                'reward_amount': 1500.00,
                'advance_referrals_required': 0,
                'pro_referrals_required': 0,
                'condition_text': 'No specific conditions required',
                'order': 1
            },
            {
                'referrals_required': 20,
                'reward_name': 'Perfume + Wallet',
                'reward_amount': 3000.00,
                'advance_referrals_required': 0,
                'pro_referrals_required': 0,
                'condition_text': 'No specific conditions required',
                'order': 2
            },
            {
                'referrals_required': 50,
                'reward_name': 'Powerbank',
                'reward_amount': 7000.00,
                'advance_referrals_required': 0,
                'pro_referrals_required': 0,
                'condition_text': 'No specific conditions required',
                'order': 3
            },
            {
                'referrals_required': 100,
                'reward_name': 'Tour Package',
                'reward_amount': 15000.00,
                'advance_referrals_required': 5,
                'pro_referrals_required': 5,
                'condition_text': 'Minimum 5 Advance Plan + 5 Pro Plan referrals required',
                'order': 4
            },
            {
                'referrals_required': 300,
                'reward_name': 'Mobile Phone',
                'reward_amount': 50000.00,
                'advance_referrals_required': 20,
                'pro_referrals_required': 20,
                'condition_text': 'Minimum 20 Advance Plan + 20 Pro Plan referrals required',
                'order': 5
            },
            {
                'referrals_required': 500,
                'reward_name': 'Motorcycle',
                'reward_amount': 90000.00,
                'advance_referrals_required': 30,
                'pro_referrals_required': 30,
                'condition_text': 'Minimum 30 Advance Plan + 30 Pro Plan referrals required',
                'order': 6
            },
            {
                'referrals_required': 1000,
                'reward_name': 'Umrah Package',
                'reward_amount': 200000.00,
                'advance_referrals_required': 70,
                'pro_referrals_required': 70,
                'condition_text': 'Minimum 70 Advance Plan + 70 Pro Plan referrals required',
                'order': 7
            }
        ]
        
        # Create rewards
        created_count = 0
        for reward_data in rewards_data:
            reward = TeamReward.objects.create(**reward_data)
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Created reward: {reward.reward_name} '
                    f'({reward.referrals_required} referrals) - Rs.{reward.reward_amount:,.0f}'
                )
            )
            
            if reward.has_conditions():
                self.stdout.write(
                    f'  Conditions: {reward.advance_referrals_required} Advance + '
                    f'{reward.pro_referrals_required} Pro plans required'
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Successfully created {created_count} team rewards!'
            )
        )
        
        self.stdout.write(
            self.style.WARNING(
                '\nTeam Instructions:'
            )
        )
        self.stdout.write('1. Basic/Standard Plan referrals have no additional conditions')
        self.stdout.write('2. Rewards from 100+ referrals require specific Advance/Pro plan referrals')
        self.stdout.write('3. More premium referrals make rewards easier to achieve')