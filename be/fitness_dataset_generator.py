"""
Fitness Dataset Generator
Generates synthetic fitness Q&A data for model fine-tuning.
Supports multiple fitness goals: weight loss, muscle building, cardiovascular health, wellness, athletic performance.
"""

import json
import random
from typing import List, Dict
from datetime import datetime

# Fitness goal templates
FITNESS_GOALS = {
    "weight_loss": {
        "label": "weight_loss",
        "description": "Weight loss and fat reduction",
        "queries": [
            "How can I lose weight effectively?",
            "What exercises burn the most calories?",
            "How should I structure my diet for weight loss?",
            "What's the best cardio routine for fat loss?",
            "How often should I exercise to lose weight?",
            "Should I count calories?",
            "What foods should I avoid when losing weight?",
            "How long does it take to see weight loss results?",
            "Is strength training good for weight loss?",
            "How can I maintain muscle while losing fat?",
        ]
    },
    "muscle_building": {
        "label": "muscle_building",
        "description": "Muscle gain and strength development",
        "queries": [
            "How can I build muscle effectively?",
            "What's the best workout split for muscle growth?",
            "How much protein do I need to build muscle?",
            "What exercises build the most muscle?",
            "How often should I train each muscle group?",
            "Should I do cardio while building muscle?",
            "What supplements help with muscle growth?",
            "How long does it take to see muscle gains?",
            "What's the importance of rest for muscle building?",
            "How should I structure my meals for muscle gain?",
        ]
    },
    "cardiovascular_health": {
        "label": "cardiovascular_health",
        "description": "Heart health and endurance",
        "queries": [
            "How can I improve my heart health?",
            "What cardio is best for cardiovascular fitness?",
            "How should I structure cardio training?",
            "Can strength training improve heart health?",
            "What heart rate zones should I train in?",
            "How often should I do cardio?",
            "What's the difference between HIIT and steady-state cardio?",
            "How long does cardiovascular fitness take to improve?",
            "What foods support heart health?",
            "How does running improve cardiovascular health?",
        ]
    },
    "general_wellness": {
        "label": "general_wellness",
        "description": "Overall health, flexibility, and balance",
        "queries": [
            "How can I improve my overall fitness?",
            "What exercises improve flexibility?",
            "How should I balance strength and flexibility?",
            "What's the best beginner workout routine?",
            "How can I reduce stress through exercise?",
            "What's the importance of stretching?",
            "How can I improve my posture?",
            "What low-impact exercises are good for joints?",
            "How does yoga help fitness?",
            "What should be in a balanced fitness routine?",
        ]
    },
    "athletic_performance": {
        "label": "athletic_performance",
        "description": "Sports performance and agility",
        "queries": [
            "How can I improve my athletic performance?",
            "What training improves speed and agility?",
            "How should athletes structure their training?",
            "What recovery methods help athletic performance?",
            "How important is sport-specific training?",
            "What nutrition supports athletic performance?",
            "How can I prevent sports injuries?",
            "What mental training helps athletic performance?",
            "How should I periodize my training?",
            "What role does sleep play in athletic performance?",
        ]
    }
}

# Comprehensive fitness advice templates
FITNESS_ADVICE = {
    "weight_loss": [
        "For weight loss, focus on creating a calorie deficit through a combination of diet and exercise. Aim for 300-500 calorie deficit daily. Include both cardio (30-45 min, 3-5x/week) and strength training (2-3x/week) to preserve muscle mass.",
        "Weight loss is 80% diet and 20% exercise. Focus on whole foods, protein intake, and reducing processed foods. Track your calories using an app to stay accountable.",
        "Best exercises for weight loss: running, cycling, swimming, HIIT workouts, and circuit training. Aim for 150-300 minutes of moderate cardio weekly.",
        "Eat protein with every meal (0.8-1g per lb of body weight) to maintain satiety and preserve muscle. Include fiber-rich vegetables and complex carbs.",
        "Sleep 7-9 hours nightly and manage stress, as poor sleep increases cortisol and hunger hormones. This supports your weight loss goals significantly.",
        "Avoid rapid weight loss. Aim for 1-2 lbs per week (0.5-1 kg). This preserves muscle and is more sustainable long-term.",
        "Strength training is crucial during weight loss to maintain muscle. Do 2-3 sessions per week with compound movements.",
    ],
    "muscle_building": [
        "To build muscle, follow progressive overload: gradually increase weight/reps. Eat 0.7-1g protein per lb of body weight daily. Train each muscle group 2x per week with 3-5 exercises per session.",
        "Muscle growth requires adequate calories. Eat in a 300-500 calorie surplus with emphasis on protein and carbs. Rest days are crucial - muscles grow during recovery, not during workouts.",
        "Best exercises for muscle: squats, deadlifts, bench press, rows, and overhead press. Include 3-4 sets of 6-12 reps per exercise for hypertrophy.",
        "Recovery is essential: sleep 8+ hours, manage stress, and allow 48 hours between training the same muscle group.",
        "Include both compound movements and isolation exercises. Compounds build strength, isolation exercises target specific muscles.",
        "Carbs are important for muscle growth and energy. Eat 4-7g per kg of body weight depending on activity level.",
        "Track your progress. Aim to increase weights or reps every 1-2 weeks (progressive overload) to continue muscle growth.",
    ],
    "cardiovascular_health": [
        "Cardiovascular health improves with consistent cardio training. Aim for 150 minutes of moderate intensity or 75 minutes of vigorous intensity weekly.",
        "Train in different heart rate zones: Zone 2 (60-70% max HR) for base building, Zone 3-4 (70-85%) for aerobic capacity, Zone 5 (85%+) for peak performance.",
        "Best cardio for heart health: running, cycling, swimming, rowing, and elliptical. Mix steady-state cardio with interval training.",
        "Include strength training 2x per week. Heavy strength training also builds cardiovascular health and prevents age-related muscle loss.",
        "Monitor your resting heart rate (lower is better). A lower RHR indicates better cardiovascular fitness.",
        "Eat heart-healthy foods: fatty fish (omega-3s), whole grains, fruits, vegetables, and limit sodium and refined sugars.",
        "Recovery matters: adequate sleep, stress management, and proper hydration support cardiovascular health and prevent overtraining.",
    ],
    "general_wellness": [
        "A balanced fitness routine includes: cardio (2-3x/week), strength training (2-3x/week), flexibility work/yoga (1-2x/week), and 1-2 rest days.",
        "Flexibility and mobility prevent injuries and improve quality of life. Include 10-15 minutes of stretching or yoga in your weekly routine.",
        "Start with bodyweight exercises if you're a beginner: push-ups, squats, lunges, planks. Build a solid foundation before adding weights.",
        "Consistency beats intensity. A moderate routine done consistently (4-5x/week) beats an intense routine done occasionally.",
        "Listen to your body. Rest when needed to prevent overtraining and burnout. Active recovery (walking, yoga) helps on rest days.",
        "Nutrition supports fitness: eat balanced meals with protein, carbs, and healthy fats. Hydrate adequately throughout the day.",
        "Mental health and exercise are connected. Regular exercise reduces anxiety, stress, and improves mood and sleep quality.",
    ],
    "athletic_performance": [
        "Athletic performance improves with sport-specific training. Focus on movements and energy systems used in your sport.",
        "Include speed, agility, and plyometric work: ladder drills, cone drills, box jumps, and sport-specific drills 2-3x per week.",
        "Periodize your training: build a base (4-6 weeks), build strength (4-6 weeks), develop power (4-6 weeks), then peak and recover.",
        "Recovery is crucial for performance: sleep 8-9+ hours, use ice/heat therapy, get sports massage, and manage training load.",
        "Eat for performance: adequate carbs for energy (5-7g/kg for high training load), protein for recovery (1.2-2g/kg), and strategic timing around training.",
        "Mental training matters: visualization, goal-setting, and mental toughness training improve athletic performance.",
        "Track your metrics: speed, power, flexibility, and recovery metrics. Data-driven training improves performance more than guesswork.",
    ]
}

class FitnessDatasetGenerator:
    def __init__(self, random_seed=42):
        random.seed(random_seed)
    
    def generate_training_pairs(self, goal: str, num_samples: int = 50) -> List[Dict]:
        """Generate training pairs (prompt, response) for a specific fitness goal."""
        if goal not in FITNESS_GOALS:
            raise ValueError(f"Unknown fitness goal: {goal}")
        
        queries = FITNESS_GOALS[goal]["queries"]
        advice = FITNESS_ADVICE[goal]
        training_pairs = []
        
        for i in range(num_samples):
            query = random.choice(queries)
            response = random.choice(advice)
            
            # Create the prompt in conversation format
            prompt = f"<|system|>\nYou are a helpful fitness coach specializing in {FITNESS_GOALS[goal]['description'].lower()}.\n<|user|>\n{query}\n<|assistant|>\n"
            
            training_pairs.append({
                "prompt": prompt,
                "response": response,
                "goal": goal,
                "query": query,
                "full_text": prompt + response
            })
        
        return training_pairs
    
    def generate_multi_goal_dataset(self, samples_per_goal: int = 50) -> List[Dict]:
        """Generate a combined dataset covering all fitness goals."""
        all_data = []
        
        for goal in FITNESS_GOALS.keys():
            pairs = self.generate_training_pairs(goal, samples_per_goal)
            all_data.extend(pairs)
        
        # Shuffle to mix goals
        random.shuffle(all_data)
        return all_data
    
    def save_to_jsonl(self, training_data: List[Dict], filepath: str):
        """Save training data to JSONL format (one JSON object per line)."""
        with open(filepath, 'w') as f:
            for item in training_data:
                f.write(json.dumps(item) + '\n')
        print(f"✅ Saved {len(training_data)} training examples to {filepath}")
    
    def save_to_json(self, training_data: List[Dict], filepath: str):
        """Save training data to JSON format."""
        with open(filepath, 'w') as f:
            json.dump(training_data, f, indent=2)
        print(f"✅ Saved {len(training_data)} training examples to {filepath}")
    
    def generate_and_save(self, output_dir: str = "training_data", samples_per_goal: int = 50):
        """Generate and save all datasets."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate combined dataset
        print("📊 Generating fitness training dataset...")
        all_data = self.generate_multi_goal_dataset(samples_per_goal)
        
        # Save as JSONL (good for streaming training)
        jsonl_path = os.path.join(output_dir, "fitness_data.jsonl")
        self.save_to_jsonl(all_data, jsonl_path)
        
        # Save as JSON (good for inspection)
        json_path = os.path.join(output_dir, "fitness_data.json")
        self.save_to_json(all_data, json_path)
        
        # Save individual goal datasets
        for goal in FITNESS_GOALS.keys():
            goal_data = [d for d in all_data if d["goal"] == goal]
            goal_path = os.path.join(output_dir, f"fitness_data_{goal}.jsonl")
            self.save_to_jsonl(goal_data, goal_path)
        
        print(f"📁 All datasets saved to {output_dir}/")
        return all_data, output_dir


if __name__ == "__main__":
    generator = FitnessDatasetGenerator()
    
    # Generate 50 samples per fitness goal (250 total)
    all_data, output_dir = generator.generate_and_save(
        output_dir="training_data",
        samples_per_goal=50
    )
    
    print(f"\n📈 Dataset Summary:")
    print(f"   Total samples: {len(all_data)}")
    print(f"   Samples per goal: {len(all_data) // len(FITNESS_GOALS)}")
    print(f"   Fitness goals covered: {', '.join(FITNESS_GOALS.keys())}")
