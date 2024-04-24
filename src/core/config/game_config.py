from item.models import EffectProperty

EXP_RATE = 1
DROP_RATE = 1
EXP_DECREASE_PERCENT = 5

LOCATION_STAT_DIFFERENCE = 3
HUNTING_ALERT_HOURS = 4

# Эффекты в процентах добавляются первыми
IN_PERCENT_MODIFIER_FIRST = True


MAX_HEALTH_DEFAULT = 24
MAX_MANA_DEFAULT = 16
ACCURACY_DEFAULT = 10
EVASION_DEFAULT = 10
CRIT_RATE_DEFAULT = 50
CRIT_POWER_DEFAULT = 50

EXP_FOR_LEVEL_UP_MULTIPLIER = 1.5
ATTACK_INCREASE_LEVEL_UP = 4
DEFENCE_INCREASE_LEVEL_UP = 4
ACCURACY_INCREASE_LEVEL_UP = 1
EVASION_INCREASE_LEVEL_UP = 1
HEALTH_INCREASE_LEVEL_UP = 12
MANA_INCREASE_LEVEL_UP = 8

ENHANCE_CHANCE = [
    80,
    70,
    60,
    50,
    40,
    30,
    20,
    10,
]

ENHANCE_INCREASE = 4
ENHANCE_IN_PERCENT_INCREASE = 5

NOT_ENHANCE_PROPERTY_DATA = [EffectProperty.EVASION, EffectProperty.ACCURACY]

MARKETPLACE_TAX = 10
MAX_LOT_AMOUNT = 5

MASTER_SHOP_TAX = 10
MAX_RECIPE_AMOUNT = 10

PREMIUM_EXP_MODIFIER = 2
PREMIUM_DROP_MODIFIER = 1.5
PREMIUM_DEATH_EXP_MODIFIER = 0.5

WAR_EXP_DECREASE_PERCENT = 1
WAR_END_REPUTATION_COST = 100
REPUTATION_AMOUNT_BY_LEVEL = 5
EVASION_CHANCE_BY_POINT = 5

MINUTES_FOR_ENTER_CLAN_RAID = 1
RESPAWN_HOURS_LOCATION_BOSS = 12
RESPAWN_HOURS_CLAN_BOSS = 24

RESET_POWER_DIAMOND_COST = 50
