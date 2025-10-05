# Afaa Elevate - Team Rewards System

## Team Rewards Setup Complete! ✅

All team rewards have been set up according to your specifications. Here's the complete breakdown:

### Reward Tiers:

#### 🎁 **10 Referrals** - Watch (Rs.1,500)
- **Condition:** No additional conditions
- **Requirement:** Any 10 referrals (Basic/Standard/Advance/Pro)

#### 🎁 **20 Referrals** - Perfume + Wallet (Rs.3,000)
- **Condition:** No additional conditions  
- **Requirement:** Any 20 referrals (Basic/Standard/Advance/Pro)

#### 🎁 **50 Referrals** - Powerbank (Rs.7,000)
- **Condition:** No additional conditions
- **Requirement:** Any 50 referrals (Basic/Standard/Advance/Pro)

#### 🎁 **100 Referrals** - Tour Package (Rs.15,000)
- **Condition:** 5+ Advance Plan + 5+ Pro Plan referrals required
- **Requirement:** Total 100 referrals with at least 5 Advance and 5 Pro

#### 🎁 **300 Referrals** - Mobile Phone (Rs.50,000)
- **Condition:** 20+ Advance Plan + 20+ Pro Plan referrals required
- **Requirement:** Total 300 referrals with at least 20 Advance and 20 Pro

#### 🎁 **500 Referrals** - Motorcycle (Rs.90,000)
- **Condition:** 30+ Advance Plan + 30+ Pro Plan referrals required
- **Requirement:** Total 500 referrals with at least 30 Advance and 30 Pro

#### 🎁 **1000 Referrals** - Umrah Package (Rs.2,00,000)
- **Condition:** 70+ Advance Plan + 70+ Pro Plan referrals required
- **Requirement:** Total 1000 referrals with at least 70 Advance and 70 Pro

---

### Team Instructions:

1. **Basic/Standard Plan referrals** have no additional conditions
2. **Rewards from 100+ referrals** require specific Advance/Pro plan referrals
3. **More premium referrals** make rewards easier to achieve
4. All rewards are active and will be automatically tracked
5. Users can see their progress towards each reward in their dashboard

---

### Management Commands:

To reset and recreate all rewards:
```bash
python manage.py setup_team_rewards
```

This will clear all existing rewards and create the new ones as specified.

---

### Technical Notes:

- Rewards are automatically calculated based on referral counts
- The system tracks both total referrals and premium plan referrals separately
- Progress tracking is built into the UserProfile model
- Rewards can be managed through the admin panel if needed