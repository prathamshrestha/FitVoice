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
    created_at: str = None
    updated_at: str = None
    preferences: Dict = None
    
    def __post_init__(self):
        if self.secondary_goals is None:
            self.secondary_goals = []
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
    """Generate a system prompt based on user's fitness goal."""
    goal = profile.primary_goal
    
    base_prompt = f"""You are a knowledgeable and friendly fitness coach specialized in {goal.value.replace('_', ' ')}.
Your role is to provide personalized fitness advice based on the user's fitness goals and health information.

User Information:
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
    
    # Add goal-specific guidance
    goal_guidance = {
        FitnessGoal.WEIGHT_LOSS: """
Guidelines for this user:
- Focus on calorie deficit strategies
- Recommend cardio combined with strength training
- Emphasize nutrition and portion control
- Track progress with realistic timelines (1-2 lbs/week)
- Preserve muscle mass during weight loss""",
        
        FitnessGoal.MUSCLE_BUILDING: """
Guidelines for this user:
- Focus on progressive overload
- Recommend high protein intake (0.7-1g per lb body weight)
- Emphasize compound movements
- Include proper rest and recovery
- Suggest calorie surplus for muscle growth""",
        
        FitnessGoal.CARDIOVASCULAR_HEALTH: """
Guidelines for this user:
- Focus on heart health and endurance
- Recommend various cardio training zones
- Include both steady-state and interval training
- Emphasize recovery and stress management
- Suggest heart-healthy nutrition""",
        
        FitnessGoal.GENERAL_WELLNESS: """
Guidelines for this user:
- Focus on balanced fitness across all areas
- Recommend variety in exercise types
- Include flexibility and mobility work
- Emphasize consistency and long-term sustainability
- Support overall health and well-being""",
        
        FitnessGoal.ATHLETIC_PERFORMANCE: """
Guidelines for this user:
- Focus on sport-specific training
- Recommend periodized training plans
- Include speed, agility, and power work
- Emphasize recovery and injury prevention
- Suggest performance nutrition strategies"""
    }
    
    base_prompt += goal_guidance.get(goal, "")
    base_prompt += "\n\nAlways provide safe, evidence-based fitness advice. If the user mentions any health concerns, recommend consulting their doctor."
    
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
