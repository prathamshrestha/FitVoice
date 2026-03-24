"""
Comprehensive Fitness Knowledge Base Generator
Creates detailed fitness knowledge covering nutrition, workouts, health, and recovery
"""

import json
from typing import List, Dict

class FitnessKnowledgeBase:
    """Generates comprehensive fitness knowledge base"""
    
    def __init__(self):
        self.knowledge = {
            "nutrition": self._nutrition_knowledge(),
            "workouts": self._workout_knowledge(),
            "health": self._health_knowledge(),
            "recovery": self._recovery_knowledge(),
        }
    
    def _nutrition_knowledge(self) -> List[Dict]:
        """Detailed nutrition guidelines and facts"""
        return [
            # Macronutrients
            {"category": "macronutrients", "title": "Protein Requirements", "content": "Daily protein intake: 0.8g per kg body weight (sedentary), 1.2-2.0g per kg (active). For muscle building: 1.6-2.2g per kg. Protein sources: chicken, fish, eggs, Greek yogurt, tofu, beans, nuts."},
            {"category": "macronutrients", "title": "Carbohydrate Guidelines", "content": "Carbs provide energy for workouts. General intake: 3-5g per kg for moderate activity, 6-10g per kg for endurance sports. Complex carbs: oats, brown rice, sweet potatoes, whole wheat. Timing: consume carbs before/after workouts."},
            {"category": "macronutrients", "title": "Healthy Fats", "content": "20-35% of daily calories from fats. Omega-3 sources: salmon, sardines, flax seeds, walnuts. Avoid trans fats. Monounsaturated fats: olive oil, avocado. Benefits: hormone production, nutrient absorption, brain health."},
            
            # Micronutrients
            {"category": "micronutrients", "title": "Iron and Oxygen", "content": "Iron crucial for oxygen transport. Red meat, spinach, lentils, dark chocolate. Deficiency: fatigue, weakness. Females need 18mg/day, males 8mg/day. Vitamin C increases absorption."},
            {"category": "micronutrients", "title": "Calcium and Bone Health", "content": "1000-1200mg daily calcium for adults. Dairy (milk, yogurt, cheese), leafy greens, fortified foods. Vitamin D needed for absorption: sunlight, salmon, eggs. Critical for athletes to prevent stress fractures."},
            {"category": "micronutrients", "title": "Electrolytes and Hydration", "content": "Sodium, potassium, magnesium regulate muscle function. Banana (potassium), coconut water (electrolytes). Dehydration reduces performance by 10%. Drink 500ml water per kg body weight daily."},
            
            # Meal Planning
            {"category": "meals", "title": "Pre-Workout Nutrition", "content": "60-90 min before: balanced meal with carbs + protein. Example: toast with peanut butter, oatmeal with berries, banana with almonds. Hydrate: 400-600ml water. Avoid: high fat, high fiber (causes cramping)."},
            {"category": "meals", "title": "Post-Workout Nutrition", "content": "Within 30-60 min after workout: protein + carbs to aid recovery. Ideal ratio: 1:3 or 1:4 (protein:carbs). Example: chicken with rice, protein shake with banana, Greek yogurt with granola."},
            {"category": "meals", "title": "Daily Meal Timing", "content": "5-6 small meals or 3 main + 2-3 snacks optimal for muscle building. Breakfast within 1 hour of waking. Don't skip meals - consistent intake supports metabolism. Last meal 2-3 hours before bed."},
            
            # Specific Goals
            {"category": "goals", "title": "Weight Loss Nutrition", "content": "Caloric deficit of 300-500 calories/day (0.5-1kg loss/week). High protein (1.6-2.2g/kg) preserves muscle. Whole foods, high fiber (controls hunger). Meal prep to avoid impulsive choices. Track calories initially."},
            {"category": "goals", "title": "Muscle Building Nutrition", "content": "Caloric surplus of 300-500 calories/day. Protein: 1.6-2.2g/kg daily. Carbs for energy during workouts. Creatine monohydrate: 5g daily (safe, effective). Consistent diet + training = results in 8-12 weeks."},
            {"category": "goals", "title": "Endurance Athlete Nutrition", "content": "High carbohydrate diet: 6-10g per kg body weight. Sodium during long exercise (>90min) to maintain hydration. Chia seeds, dates for sustained energy. Recovery nutrition critical: refuel within 30 min of finishing."},
        ]
    
    def _workout_knowledge(self) -> List[Dict]:
        """Detailed workout and exercise guidelines"""
        return [
            # Exercise Types
            {"category": "exercise_types", "title": "Strength Training Basics", "content": "Resistance training builds muscle and bone density. Progressive overload: gradually increase weight/reps/sets. Rest 48-72 hours between same muscle groups. 6-12 reps per set for muscle growth, 1-5 for strength. Compound lifts (squats, deadlifts, bench press) most effective."},
            {"category": "exercise_types", "title": "Cardiovascular Exercise", "content": "150 min moderate-intensity or 75 min high-intensity weekly. Moderate: 50-70% max heart rate, can talk but not sing. High: 70-85% max heart rate, hard to talk. Types: running, cycling, swimming, rowing. Mix steady-state and intervals."},
            {"category": "exercise_types", "title": "Flexibility and Mobility", "content": "Stretching improves range of motion, reduces injury risk. Static stretching post-workout (hold 30s), dynamic pre-workout (controlled movement). Yoga, foam rolling improve mobility. 10-15 min daily recommended. Improves exercise performance and recovery."},
            
            # Goal-Specific Workouts
            {"category": "programs", "title": "Weight Loss Workout Plan", "content": "Mix strength (3x/week) + cardio (3-4x/week). HIIT: 20s high-intensity, 40s recovery, 10-15 minutes. Circuit training: minimal rest between exercises. Track sessions to maintain consistency. Progressive: increase duration or intensity monthly."},
            {"category": "programs", "title": "Muscle Building Program", "content": "Progressive overload structured: increase weight 2-5% when 12 reps completed easily. Split routine: chest, back, legs, shoulders (each 2x/week). 8-12 reps per set, 3-4 sets per exercise. Rest 60-90s between sets. Sleep 7-9 hours for recovery."},
            {"category": "programs", "title": "Athletic Performance Training", "content": "Explosive movements: plyometrics (jump squats, box jumps). Sport-specific drills. Strength + power focus. Olympic lifts: clean & jerk, snatch for power. Agility ladder for footwork. 4-6 weeks strength block, 2-3 weeks taper before competition."},
            
            # Exercise Techniques
            {"category": "techniques", "title": "Proper Squat Form", "content": "Feet shoulder-width apart, toes slightly out. Lower slowly, knees tracking over toes, chest up. Hip crease drops below parallel. Weight in heels. Return to standing. Common error: knees caving inward. Start bodyweight, progress to barbell."},
            {"category": "techniques", "title": "Deadlift Execution", "content": "Feet hip-width, shins vertical. Grab bar just outside legs. Neutral spine, chest up. Pull bar in straight line close to body. Drive through heels. Full hip extension at top. Return with control. Cue: chest up, straight bar path, glutes tight."},
            {"category": "techniques", "title": "Bench Press Safety", "content": "Back on bench, feet planted on floor. Grip slightly wider than shoulders. Lower bar to chest, elbows 45° from body. Press up explosively. Full range of motion. Spot for safety above chest. Progress weight gradually to prevent shoulder injury."},
            
            # Programming
            {"category": "programming", "title": "Rest Days Importance", "content": "Muscles grow during rest, not during workouts. Minimum 1-2 rest days weekly. Active recovery: light walking, stretching, yoga improves blood flow. Overtraining leads to injury, plateaus. Monitor: resting heart rate (elevated = underrecovered), soreness, mood."},
            {"category": "programming", "title": "Periodization for Progress", "content": "4-week blocks: hypertrophy (8-12 reps), strength (3-6 reps), power (explosive). Cycle prevents plateaus, optimizes adaptation. Deload week (reduce volume 40-60%) improves recovery. Periodization increases long-term gains vs constant routine."},
        ]
    
    def _health_knowledge(self) -> List[Dict]:
        """Health, wellness, and medical guidelines"""
        return [
            # General Health
            {"category": "general_health", "title": "Sleep and Recovery", "content": "Adults need 7-9 hours nightly for optimal health. Sleep affects: hormone production, muscle recovery, immune function, mood. Blue light before bed disrupts sleep. Cool, dark room optimal. Sleep tracks progress of fitness goals."},
            {"category": "general_health", "title": "Stress Management", "content": "Chronic stress increases cortisol, reduces muscle growth, increases belly fat. Techniques: meditation, deep breathing, exercise, hobbies. 10-15 min daily meditation improves focus. Exercise is excellent stress relief, but overtraining adds stress."},
            {"category": "general_health", "title": "Hydration Guidelines", "content": "Drink 30-35ml per kg body weight daily (minimum). Increase for: hot weather, exercise, high altitude. Dehydration: reduced strength (10%), endurance (30%), cognitive function. Urine color indicator: pale yellow = hydrated, dark = drink more."},
            
            # Injury Prevention
            {"category": "injury_prevention", "title": "Common Fitness Injuries", "content": "Knee pain: incorrect form, overtraining. Back injury: poor posture, weak core. Shoulder impingement: weak rotator cuff. Prevention: proper form, progressive overload, mobility work, adequate recovery. Treatment: RICE (Rest, Ice, Compression, Elevation), PT."},
            {"category": "injury_prevention", "title": "Warming Up Correctly", "content": "5-10 min warm-up before workout. Dynamic stretching: leg swings, arm circles, bodyweight movements. Increases heart rate, blood flow to muscles. Reduces injury risk, improves performance. Cold muscles more prone to acute injuries."},
            {"category": "injury_prevention", "title": "Listening to Body Signals", "content": "Pain: stop immediately, assess injury. Soreness vs injury: soreness is normal post-workout (DOMS), injury is sharp/localized. Joint pain = reduce volume/intensity. Rest, ice, compression for acute injury. Seek PT if pain persists >2 weeks."},
            
            # Age and Special Populations
            {"category": "special_populations", "title": "Fitness for Older Adults", "content": "50+: focus on strength (falls prevention), balance, flexibility. 2x strength training weekly (lighter weights, higher reps). Low-impact cardio: walking, swimming, cycling. Bone density check important. Benefits: independence, cognitive health, reduced disease risk."},
            {"category": "special_populations", "title": "Post-Pregnancy Exercise", "content": "6-8 weeks after vaginal delivery before exercise (10-12 weeks after C-section). Start with walking, pelvic floor exercises. Avoid heavy lifting initially. Breastfeeding affects hydration needs. Energy deficit not recommended while nursing. Postpartum depression: exercise helps."},
            {"category": "special_populations", "title": "Exercise During Menopause", "content": "Strength training combats muscle/bone loss. 150 min cardio weekly. Hydration critical (hot flashes). Flexibility prevents stiffness. Weight management harder (lower estrogen). Sleep quality improves with regular exercise. Consult doctor before starting new program."},
            
            # Medical Conditions
            {"category": "medical", "title": "Exercise with Diabetes", "content": "Type 1: monitor blood sugar, avoid injecting into muscles being exercised. Type 2: exercise improves insulin sensitivity, reduces medications needed. 150 min moderate activity weekly optimal. Hydration crucial. Avoid exercise at peak insulin time."},
            {"category": "medical", "title": "High Blood Pressure Management", "content": "Exercise reduces BP 5-8 mmHg. Aerobic: 150 min/week moderate or 75 min high-intensity. Strength training: safe, 2x weekly. Avoid isometric exercises (holding positions). Reduce sodium, increase potassium. Medications may need adjustment with exercise."},
            {"category": "medical", "title": "Back Pain and Exercise", "content": "Core strengthening: planks, dead bugs, bird dogs. Avoid heavy forward bending (deadlifts). Swimming, walking low-impact. Flexibility: yoga, stretching. Posture awareness crucial. 6-8 weeks dedicated core training often resolves pain."},
        ]
    
    def _recovery_knowledge(self) -> List[Dict]:
        """Recovery and performance optimization"""
        return [
            # Recovery Methods
            {"category": "recovery_methods", "title": "Active Recovery Days", "content": "Low-intensity activities: walking, light yoga, swimming, foam rolling. 30% of max heart rate. Improves blood flow, removes metabolic waste. Reduces next-day soreness (DOMS). 1-2 times weekly optimal. Accelerates adaptation to training."},
            {"category": "recovery_methods", "title": "Massage and Foam Rolling", "content": "Alleviates muscle tension, improves blood flow. Foam roll 60-90s per muscle group. Self-massage: lacrosse ball on trigger points. Professional massage: 1-2 times monthly after hard training blocks. Cost-benefit: prevents injury, improves mobility."},
            {"category": "recovery_methods", "title": "Contrast Water Therapy", "content": "Alternate hot/cold water: 3 min hot, 1 min cold, repeat 5 times. Increases blood flow, reduces inflammation. Research mixed but feels good subjectively. Ice baths: extreme soreness recovery (2-4°C, 10-15 min). Not for general training."},
            
            # Sleep Optimization
            {"category": "sleep", "title": "Sleep Protocol for Athletes", "content": "Consistency: same bedtime/wake time. Environment: 65-68°F, dark, quiet. Supplements: magnesium, glycine optional. Avoid: caffeine after 2pm, alcohol before bed, screens 1 hour before. Track: sleep quantity, quality. Aim: 8-10 hours for athletes in heavy training."},
            {"category": "sleep", "title": "Napping Benefits", "content": "20-30 min power nap: improves alertness, performance without sleep inertia. 90 min nap: includes full sleep cycle, more restorative. Post-workout nap optimal (within 4 hours). Before training: limit to 20 min (don't oversleep). Naps don't replace nighttime sleep."},
            
            # Supplementation
            {"category": "supplementation", "title": "Evidence-Based Supplements", "content": "Creatine monohydrate: 5g daily increases strength, muscle mass. Protein powder: convenient, if diet insufficient. Caffeine: 3-6mg per kg body weight, 30 min before workout improves performance. Vitamin D: deficiency common, 1000-4000 IU daily. Omega-3: joint health, inflammation."},
            {"category": "supplementation", "title": "When to Supplement", "content": "Start: whole food diet first. Add when: diet lacks nutrients, cost-effective, research-backed. Avoid: unproven supplements, excessive protein powder. Test: try for 4-8 weeks, measure effect on performance/physique. Most gains from training + nutrition, not supplements."},
            
            # Performance Monitoring
            {"category": "monitoring", "title": "Tracking Progress Metrics", "content": "Strength: record weights/reps, aim 2-5% increase monthly. Endurance: track pace, distance, heart rate trends. Muscle: measure body parts, track progress photos (monthly). Scales misleading: muscle weighs more. Body composition more accurate (DEXA scan)."},
            {"category": "monitoring", "title": "Heart Rate Variability (HRV)", "content": "HRV indicates recovery status: higher HRV = recovered. Lower HRV = underrecovered, increase rest. Apps: Whoop, Apple Watch estimate HRV. Resting heart rate trending up = overtraining. Progressive overload when HRV good."},
        ]
    
    def get_all_knowledge(self) -> List[Dict]:
        """Return flattened knowledge base"""
        all_docs = []
        for category_docs in self.knowledge.values():
            all_docs.extend(category_docs)
        return all_docs
    
    def save_to_jsonl(self, filepath: str):
        """Save knowledge base to JSONL format"""
        all_docs = self.get_all_knowledge()
        with open(filepath, 'w') as f:
            for doc in all_docs:
                f.write(json.dumps(doc) + '\n')
        print(f"✅ Saved {len(all_docs)} knowledge documents to {filepath}")
        return len(all_docs)
    
    def get_knowledge_by_category(self, category: str) -> List[Dict]:
        """Get knowledge by specific category"""
        results = []
        for cat_docs in self.knowledge.values():
            results.extend([d for d in cat_docs if d.get('category') == category])
        return results


if __name__ == "__main__":
    kb = FitnessKnowledgeBase()
    all_docs = kb.get_all_knowledge()
    print(f"📚 Fitness Knowledge Base: {len(all_docs)} documents")
    
    # Display sample
    print("\n🔍 Sample knowledge documents:\n")
    for doc in all_docs[:3]:
        print(f"  {doc['title']}: {doc['content'][:80]}...")
    
    # Save to file
    kb.save_to_jsonl("fitness_knowledge_base.jsonl")
