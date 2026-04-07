"""
User Profile System for FitVoice
Manages user fitness goals and preferences
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
from enum import Enum
import json
from datetime import datetime
from pathlib import Path


class FitnessGoal(str, Enum):
    """Supported fitness goals."""
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_BUILDING = "muscle_building"
    CARDIOVASCULAR_HEALTH = "cardiovascular_health"
    GENERAL_WELLNESS = "general_wellness"
    ATHLETIC_PERFORMANCE = "athletic_performance"


@dataclass
class UserProfile:
    """User fitness profile."""
    user_id: str
    name: str
    age: Optional[int] = None
    fitness_level: Optional[str] = None  # beginner, intermediate, advanced
    primary_goal: FitnessGoal = FitnessGoal.GENERAL_WELLNESS
    secondary_goals: List[FitnessGoal] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    medical_conditions: Optional[str] = None
    dietary_restrictions: List[str] = None  # e.g., ["vegetarian", "gluten-free", "dairy-free"]
    created_at: str = None
    updated_at: str = None
    preferences: Dict = None
    
    def __post_init__(self):
        if self.secondary_goals is None:
            self.secondary_goals = []
        if self.dietary_restrictions is None:
            self.dietary_restrictions = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        if self.preferences is None:
            self.preferences = {}
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary."""
        data = asdict(self)
        data["primary_goal"] = self.primary_goal.value
        data["secondary_goals"] = [g.value for g in self.secondary_goals]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> "UserProfile":
        """Create profile from dictionary."""
        # Convert string values back to enums
        if isinstance(data.get("primary_goal"), str):
            data["primary_goal"] = FitnessGoal(data["primary_goal"])
        if data.get("secondary_goals"):
            data["secondary_goals"] = [
                FitnessGoal(g) if isinstance(g, str) else g
                for g in data["secondary_goals"]
            ]
        return cls(**data)


class UserProfileManager:
    """Manages user profiles and persistence."""
    
    def __init__(self, profiles_dir: str = "user_profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        self.profiles: Dict[str, UserProfile] = {}
        self._load_all_profiles()
    
    def _get_profile_path(self, user_id: str) -> Path:
        """Get file path for user profile."""
        return self.profiles_dir / f"{user_id}.json"
    
    def create_profile(
        self,
        user_id: str,
        name: str,
        primary_goal: FitnessGoal = FitnessGoal.GENERAL_WELLNESS,
        **kwargs
    ) -> UserProfile:
        """Create a new user profile."""
        profile = UserProfile(
            user_id=user_id,
            name=name,
            primary_goal=primary_goal,
            **kwargs
        )
        self.profiles[user_id] = profile
        self.save_profile(user_id)
        print(f"✅ Created profile for {name} (Goal: {primary_goal.value})")
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID."""
        return self.profiles.get(user_id)
    
    def update_profile(
        self,
        user_id: str,
        **kwargs
    ) -> Optional[UserProfile]:
        """Update user profile."""
        profile = self.profiles.get(user_id)
        if not profile:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_at = datetime.now().isoformat()
        self.save_profile(user_id)
        print(f"✅ Updated profile for {user_id}")
        return profile
    
    def save_profile(self, user_id: str) -> bool:
        """Save profile to disk."""
        profile = self.profiles.get(user_id)
        if not profile:
            return False
        
        profile_path = self._get_profile_path(user_id)
        with open(profile_path, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
        return True
    
    def _load_all_profiles(self):
        """Load all profiles from disk."""
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r') as f:
                    data = json.load(f)
                    profile = UserProfile.from_dict(data)
                    self.profiles[profile.user_id] = profile
            except Exception as e:
                print(f"⚠️ Error loading profile {profile_file}: {e}")
    
    def list_all_profiles(self) -> List[UserProfile]:
        """List all user profiles."""
        return list(self.profiles.values())
    
    def delete_profile(self, user_id: str) -> bool:
        """Delete a user profile."""
        if user_id not in self.profiles:
            return False
        
        del self.profiles[user_id]
        profile_path = self._get_profile_path(user_id)
        if profile_path.exists():
            profile_path.unlink()
        print(f"✅ Deleted profile for {user_id}")
        return True


def get_goal_specific_system_prompt(profile: UserProfile) -> str:
    """Generate a system prompt based on user's fitness goal and profile info with STRICT dietary enforcement."""
    goal = profile.primary_goal
    
    # START WITH DIETARY RESTRICTIONS AS PRIMARY CONSTRAINT
    base_prompt = ""
    
    if profile.dietary_restrictions:
        restrictions_str = ", ".join(profile.dietary_restrictions)
        base_prompt = f"""IMPORTANT: This user is {restrictions_str}. YOU MUST ALWAYS tailor ALL nutrition recommendations to ONLY include foods that are {restrictions_str}.

"""
    
    base_prompt += f"""You are a knowledgeable and friendly fitness coach specialized in {goal.value.replace('_', ' ')}.
Your role is to provide personalized, tailored fitness advice for {profile.name}.

USER PROFILE:
- Name: {profile.name}
- Fitness Level: {profile.fitness_level or 'Not specified'}
- Primary Goal: {goal.value.replace('_', ' ')}
- Secondary Goals: {', '.join(g.value.replace('_', ' ') for g in profile.secondary_goals) if profile.secondary_goals else 'None'}"""
    
    # Add health information if available
    if profile.age:
        base_prompt += f"\n- Age: {profile.age}"
    if profile.weight_kg:
        base_prompt += f"\n- Weight: {profile.weight_kg}kg"
    if profile.height_cm:
        base_prompt += f"\n- Height: {profile.height_cm}cm"
    if profile.medical_conditions:
        base_prompt += f"\n- Medical Conditions: {profile.medical_conditions}"
    if profile.dietary_restrictions:
        base_prompt += f"\n- Dietary Restrictions: {', '.join(profile.dietary_restrictions)} ← MUST RESPECT THIS"
    
    # Add SPECIFIC goal-specific guidance WITH dietary integration
    if goal == FitnessGoal.MUSCLE_BUILDING:
        if profile.dietary_restrictions and any('vegan' in r.lower() for r in profile.dietary_restrictions):
            base_prompt += """

MUSCLE BUILDING GUIDELINES FOR VEGAN DIET:
- Target: 1.6-2.2g protein per kg body weight DAILY (from VEGAN sources only!)
- VEGAN PROTEIN SOURCES: Tofu, tempeh, seitan, legumes (beans, lentils, chickpeas), nuts, seeds, pea protein powder
- Combine proteins for complete amino acids: rice + beans, tofu + seeds, nuts + legumes
- Include creatine supplementation (vegan creatine available)
- NEVER recommend meat, fish, eggs, dairy, or whey protein
- Example daily proteins: Oatmeal with peanut butter, tofu stir-fry with brown rice and legumes, lentil pasta
- Focus on progressive overload with compound movements
- Adequate rest and recovery is critical"""
        elif profile.dietary_restrictions and any('vegetarian' in r.lower() for r in profile.dietary_restrictions):
            base_prompt += """

MUSCLE BUILDING GUIDELINES FOR VEGETARIAN DIET:
- Target: 1.6-2.2g protein per kg body weight DAILY
- PROTEIN SOURCES: Eggs, Greek yogurt, cottage cheese, legumes, nuts, seeds, plant-based proteins
- Can include dairy for additional protein and creatine
- Focus on progressive overload with compound movements
- Adequate rest and recovery is critical"""
        else:
            base_prompt += """

MUSCLE BUILDING GUIDELINES:
- Target: 1.6-2.2g protein per kg body weight DAILY
- High protein intake for muscle repair and growth
- Emphasize compound movements (squats, deadlifts, bench press)
- Include proper rest and recovery
- Calorie surplus for muscle growth"""
    
    elif goal == FitnessGoal.WEIGHT_LOSS:
        base_prompt += """

WEIGHT LOSS GUIDELINES:
- Create calorie deficit of 300-500 calories per day
- Maintain high protein (0.8-1g per lb) to preserve muscle
- Combine cardio with strength training
- Track progress with realistic timelines (1-2 lbs/week)
- Sustainable habit formation is key"""
    
    elif goal == FitnessGoal.CARDIOVASCULAR_HEALTH:
        base_prompt += """

CARDIOVASCULAR HEALTH GUIDELINES:
- Include both steady-state and interval cardio training
- Heart rate zones: Low intensity (60-70%), Moderate (70-80%), High (80-90%)
- Include strength training 2-3x per week
- Emphasize recovery and stress management
- Anti-inflammatory foods are beneficial"""
    
    elif goal == FitnessGoal.GENERAL_WELLNESS:
        base_prompt += """

GENERAL WELLNESS GUIDELINES:
- Focus on balanced fitness across cardio, strength, and flexibility
- Include variety in exercise types to prevent boredom
- Consistency over intensity
- Long-term sustainable habits
- Mind-body connection (yoga, meditation optional)"""
    
    elif goal == FitnessGoal.ATHLETIC_PERFORMANCE:
        base_prompt += """

ATHLETIC PERFORMANCE GUIDELINES:
- Sport-specific periodized training plans
- Include speed, agility, and power work
- Recovery and injury prevention critical
- Performance nutrition strategies specific to sport
- Progressive periodization phases"""
    
    # Add detailed dietary guidance for restrictions
    if profile.dietary_restrictions:
        restrictions_lower = [r.lower() for r in profile.dietary_restrictions]
        
        base_prompt += "\n\n--- MANDATORY DIETARY GUIDELINES ---"
        
        for restriction in profile.dietary_restrictions:
            restriction_lower = restriction.lower()
            
            if 'vegan' in restriction_lower:
                base_prompt += """
VEGAN REQUIREMENTS:
- NEVER recommend: Meat, poultry, fish, eggs, milk, cheese, yogurt, honey, whey protein
- ALWAYS recommend: Legumes, tofu, tempeh, seitan, nuts, seeds, whole grains, vegetables, fruits, plant-based protein powder
- For protein: Pea protein, hemp protein, brown rice protein, soy protein are excellent
- For B12: Fortified plant milks or supplements
- For iron: Lentils, spinach, pumpkin seeds (pair with vitamin C)
- For calcium: Fortified plant milks, leafy greens, tahini"""
            
            elif 'vegetarian' in restriction_lower:
                base_prompt += """
VEGETARIAN REQUIREMENTS:
- NEVER recommend: Meat, poultry, fish
- CAN recommend: Eggs, dairy, legumes, nuts, seeds
- Protein sources: Eggs, Greek yogurt, cottage cheese, tofu, legumes, nuts
- Complete proteins: Dairy + any plant protein, eggs + grains"""
            
            elif 'gluten' in restriction_lower:
                base_prompt += """
GLUTEN-FREE REQUIREMENTS:
- NEVER recommend: Wheat, barley, rye, regular bread, pasta, cereals
- ALWAYS recommend: Rice, quinoa, potatoes, corn, oats (certified GF), legumes, fruits, vegetables
- Protein: Naturally GF sources like beans, eggs, meat, fish as appropriate"""
            
            elif 'dairy' in restriction_lower:
                base_prompt += """
DAIRY-FREE REQUIREMENTS:
- NEVER recommend: Milk, cheese, yogurt, butter, cream, whey
- ALWAYS recommend: Plant-based milks (almond, soy, oat, coconut)
- Calcium sources: Fortified plant milks, leafy greens, tofu (if not vegan)
- Protein: As appropriate for other restrictions + legumes"""
    
    base_prompt += """

--- RESPONSE REQUIREMENTS ---
1. Keep responses to 2-3 sentences max (this is for voice delivery)
2. Be specific with numbers (grams, reps, sets, calories)
3. ALWAYS prioritize the user's dietary restrictions in food recommendations
4. Speak naturally and conversationally
5. Never recommend foods that violate their dietary restrictions"""
    
    return base_prompt


if __name__ == "__main__":
    # Example usage
    manager = UserProfileManager()
    
    # Create sample profiles
    profile1 = manager.create_profile(
        user_id="user_001",
        name="Alice",
        age=28,
        fitness_level="intermediate",
        primary_goal=FitnessGoal.WEIGHT_LOSS,
        secondary_goals=[FitnessGoal.GENERAL_WELLNESS],
        weight_kg=75,
        height_cm=165
    )
    
    profile2 = manager.create_profile(
        user_id="user_002",
        name="Bob",
        age=32,
        fitness_level="beginner",
        primary_goal=FitnessGoal.MUSCLE_BUILDING,
        weight_kg=80,
        height_cm=180
    )
    
    # Generate system prompt
    print("\n🎯 System Prompt for Alice:")
    print(get_goal_specific_system_prompt(profile1))
    
    print("\n" + "="*50)
    print("\n🎯 System Prompt for Bob:")
    print(get_goal_specific_system_prompt(profile2))
