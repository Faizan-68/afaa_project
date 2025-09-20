# accounts/management/commands/create_rewards.py
from django.core.management.base import BaseCommand
from accounts.models import TeamReward

class Command(BaseCommand):
    help = 'Create initial team rewards data'
    
    def handle(self, *args, **options):
        rewards_data = [
            {
                'referrals_required': 10,
                'reward_name': 'Watch Rs.1,500',
                'reward_amount': 1500,
                'advance_referrals_required': 0,
                'pro_referrals_required': 0,
                'condition_text': 'Koi condition nahi',
                'order': 1
            },
            {
                'referrals_required': 20,
                'reward_name': 'Perfume+Wallet Rs.3,000',
                'reward_amount': 3000,
                'advance_referrals_required': 0,
                'pro_referrals_required': 0,
                'condition_text': 'Koi condition nahi',
                'order': 2
            },
            {
                'referrals_required': 50,
                'reward_name': 'Powerbank Rs.7,000',
                'reward_amount': 7000,
                'advance_referrals_required': 0,
                'pro_referrals_required': 0,
                'condition_text': 'Koi condition nahi',
                'order': 3
            },
            {
                'referrals_required': 100,
                'reward_name': 'Tour Package Rs.15,000',
                'reward_amount': 15000,
                'advance_referrals_required': 5,
                'pro_referrals_required': 5,
                'condition_text': '5+ Advance Plan + 5+ Pro Plan',
                'order': 4
            },
            {
                'referrals_required': 300,
                'reward_name': 'Mobile Rs.50,000',
                'reward_amount': 50000,
                'advance_referrals_required': 20,
                'pro_referrals_required': 20,
                'condition_text': '20+ Advance Plan + 20+ Pro Plan',
                'order': 5
            },
            {
                'referrals_required': 500,
                'reward_name': 'Bike Rs.90,000',
                'reward_amount': 90000,
                'advance_referrals_required': 30,
                'pro_referrals_required': 30,
                'condition_text': '30+ Advance Plan + 30+ Pro Plan',
                'order': 6
            },
            {
                'referrals_required': 1000,
                'reward_name': 'Umrah Package Rs.2,20,000',
                'reward_amount': 200000,
                'advance_referrals_required': 70,
                'pro_referrals_required': 70,
                'condition_text': '70+ Advance Plan + 70+ Pro Plan',
                'order': 7
            }
        ]
        
        for reward_data in rewards_data:
            reward, created = TeamReward.objects.get_or_create(
                referrals_required=reward_data['referrals_required'],
                defaults=reward_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created reward: {reward.reward_name}')
                )
            else:
                # Update existing reward
                for key, value in reward_data.items():
                    if key != 'referrals_required':
                        setattr(reward, key, value)
                reward.save()
                self.stdout.write(
                    self.style.WARNING(f'Updated reward: {reward.reward_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created/updated all team rewards!')
        )