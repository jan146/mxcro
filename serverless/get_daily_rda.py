from enum import Enum

# Commonly used macro split
MACRO_SPLIT: dict[str, float] = {
    "protein": 0.25,
    "carbs": 0.45,
    "fat": 0.30,
}

class Gender(Enum):
    MALE = "m"
    FEMALE = "f"

class ActivityLevel(Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"

def get_gender(args) -> Gender:
    try:
        return Gender(args["gender"])
    except KeyError:
        raise Exception(f"Missing argument: gender")
    except ValueError as e:
        raise Exception(f"Invalid gender: {args['gender']}, allowed values: {[e.value for e in Gender]}")

def get_activity_level(args) -> ActivityLevel:
    try:
        return ActivityLevel(args["activity_level"])
    except KeyError:
        raise Exception(f"Missing argument: activity_level")
    except ValueError as e:
        raise Exception(f"Invalid activity level: {args['activity_level']}, allowed values: {[e.value for e in ActivityLevel]}")

# Basal metabolic rate
# source: https://healthycalc.com/bmr-calculator/
# height: cm, weight: kg, age: years
def get_bmr(height: float, weight: float, age: int, gender: Gender) -> float:
    match gender:
        case Gender.MALE:
            return 10.0 * weight + 6.25 * height - 5 * age + 5
        case Gender.FEMALE:
            return 10.0 * weight + 6.25 * height - 5 * age - 161
    raise Exception(f"Failed to match gender: {gender}")

# Total daily energy expenditure
# source: https://healthycalc.com/tdee-calculator/
def get_tdee(bmr: float, activity_level: ActivityLevel) -> float:
    match activity_level:
        case ActivityLevel.SEDENTARY:
            return (bmr * 1.2)
        case ActivityLevel.LIGHT:
            return (bmr * 1.375)
        case ActivityLevel.MODERATE:
            return (bmr * 1.55)
        case ActivityLevel.HIGH:
            return (bmr * 1.725)
        case ActivityLevel.VERY_HIGH:
            return (bmr * 1.9)
        case ActivityLevel.EXTREME:
            return (bmr * 2.0)
    raise Exception(f"Failed to match activity level: {activity_level}")

def main(args):
    # Parse arguments
    height: float = float(args["height"])
    weight: float = float(args["weight"])
    age: int = int(args["age"])
    try:
        gender: Gender = get_gender(args)
        activity_level: ActivityLevel = get_activity_level(args)
    except Exception as e:
        return {"error": str(e)}

    # BMR
    bmr: float = 0.0
    try:
        bmr = get_bmr(height, weight, age, gender)
    except Exception as e:
        return {"error": str(e)}

    # TDEE
    tdee: float = 0.0
    try:
        tdee = get_tdee(bmr, activity_level)
    except Exception as e:
        return {"error": str(e)}

    # Get daily RDA of macros (in grams)
    fat_calories: float = tdee * MACRO_SPLIT["fat"]
    fat: int = int(fat_calories / 9.0)
    carbs_calories: float = tdee * MACRO_SPLIT["carbs"]
    carbs: int = int(carbs_calories / 4.0)
    protein_calories: float = tdee * MACRO_SPLIT["protein"]
    protein: int = int(protein_calories / 4.0)

    # Get daily RDA of macro subcategories (in grams)
    # source: https://www.health.harvard.edu/heart-health/whats-your-daily-budget-for-saturated-fat
    fat_saturated_calories: float = min(fat_calories, tdee * 0.10)
    fat_saturated: int = int(fat_saturated_calories / 9.0)
    # source: https://ask.usda.gov/s/article/How-much-dietary-fiber-should-I-eat
    fiber: int = min(carbs, int(14.0 * (tdee / 1000.0)))
    fiber_calories: float = 4.0 * fiber
    # source: https://www.heart.org/en/healthy-living/healthy-eating/eat-smart/sugar/added-sugars
    sugar_calories: float = min(0.06 * tdee, carbs_calories - fiber_calories)
    sugar: int = int(sugar_calories / 4.0)

    # Get daily RDA of micronutrients (in milligrams)
    # source: https://www.heart.org/en/healthy-living/healthy-eating/eat-smart/sodium/how-much-sodium-should-i-eat-per-day
    sodium: int = 2300
    # source: https://www.heart.org/en/healthy-living/healthy-eating/eat-smart/sodium/potassium
    potassium: int = 2600 if gender == Gender.FEMALE else 3400
    # source: https://health.clevelandclinic.org/how-much-cholesterol-per-day
    cholesterol: int = 300

    return {
        "bmr": bmr,
        "tdee": tdee,
        "fat": fat,
        "fat_saturated": fat_saturated,
        "carbs": carbs,
        "fiber": fiber,
        "sugar": sugar,
        "protein": protein,
        "sodium": sodium,
        "potassium": potassium,
        "cholesterol": cholesterol,
    }

