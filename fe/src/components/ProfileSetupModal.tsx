import { useState } from 'react';
import { AlertCircle, Loader } from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';

export interface UserProfile {
  user_id: string;
  name: string;
  age?: number;
  fitness_level?: string;
  primary_goal: string;
  weight_kg?: number;
  height_cm?: number;
  medical_conditions?: string;
  dietary_restrictions?: string[];
}

interface ProfileSetupModalProps {
  isOpen: boolean;
  onComplete: (profile: UserProfile) => void;
  userId: string;
}

const FITNESS_LEVELS = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
];

const FITNESS_GOALS = [
  { value: 'weight_loss', label: 'Weight Loss' },
  { value: 'muscle_building', label: 'Muscle Building' },
  { value: 'cardiovascular_health', label: 'Cardiovascular Health' },
  { value: 'general_wellness', label: 'General Wellness' },
  { value: 'athletic_performance', label: 'Athletic Performance' },
];

const DIETARY_RESTRICTIONS = [
  'Vegetarian',
  'Vegan',
  'Gluten-free',
  'Dairy-free',
  'Nut-free',
  'Keto',
  'Paleo',
  'Kosher',
  'Halal',
];

export function ProfileSetupModal({ isOpen, onComplete, userId }: ProfileSetupModalProps) {
  const [formData, setFormData] = useState<UserProfile>({
    user_id: userId,
    name: '',
    age: undefined,
    fitness_level: 'beginner',
    primary_goal: 'general_wellness',
    weight_kg: undefined,
    height_cm: undefined,
    medical_conditions: '',
    dietary_restrictions: [],
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleInputChange = (field: keyof UserProfile, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleDietaryRestrictionToggle = (restriction: string) => {
    setFormData(prev => ({
      ...prev,
      dietary_restrictions: prev.dietary_restrictions?.includes(restriction)
        ? prev.dietary_restrictions.filter(r => r !== restriction)
        : [...(prev.dietary_restrictions || []), restriction]
    }));
  };

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      setError('Name is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: formData.user_id,
          name: formData.name,
          age: formData.age || null,
          fitness_level: formData.fitness_level,
          primary_goal: formData.primary_goal,
          weight_kg: formData.weight_kg || null,
          height_cm: formData.height_cm || null,
          medical_conditions: formData.medical_conditions || null,
          dietary_restrictions: formData.dietary_restrictions || [],
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create profile');
      }

      onComplete(formData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AlertDialog open={isOpen}>
      <AlertDialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <AlertDialogTitle>Welcome to FitVoice! 🎤</AlertDialogTitle>
        <AlertDialogDescription className="sr-only">
          Set up your fitness profile to get personalized recommendations
        </AlertDialogDescription>

        <div className="space-y-6 py-4">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Name *</Label>
            <Input
              id="name"
              placeholder="Your full name"
              value={formData.name}
              onChange={e => handleInputChange('name', e.target.value)}
            />
          </div>

          {/* Age and Weight/Height */}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="age">Age</Label>
              <Input
                id="age"
                type="number"
                placeholder="e.g., 25"
                value={formData.age || ''}
                onChange={e => handleInputChange('age', e.target.value ? parseInt(e.target.value) : undefined)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="weight">Weight (kg)</Label>
              <Input
                id="weight"
                type="number"
                placeholder="e.g., 70"
                step="0.1"
                value={formData.weight_kg || ''}
                onChange={e => handleInputChange('weight_kg', e.target.value ? parseFloat(e.target.value) : undefined)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="height">Height (cm)</Label>
              <Input
                id="height"
                type="number"
                placeholder="e.g., 175"
                value={formData.height_cm || ''}
                onChange={e => handleInputChange('height_cm', e.target.value ? parseFloat(e.target.value) : undefined)}
              />
            </div>
          </div>

          {/* Fitness Level */}
          <div className="space-y-2">
            <Label htmlFor="fitness-level">Fitness Level</Label>
            <Select value={formData.fitness_level} onValueChange={v => handleInputChange('fitness_level', v)}>
              <SelectTrigger id="fitness-level">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {FITNESS_LEVELS.map(level => (
                  <SelectItem key={level.value} value={level.value}>
                    {level.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Primary Goal */}
          <div className="space-y-2">
            <Label htmlFor="goal">Primary Fitness Goal *</Label>
            <Select value={formData.primary_goal} onValueChange={v => handleInputChange('primary_goal', v)}>
              <SelectTrigger id="goal">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {FITNESS_GOALS.map(goal => (
                  <SelectItem key={goal.value} value={goal.value}>
                    {goal.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Dietary Restrictions */}
          <div className="space-y-3">
            <Label>Dietary Restrictions</Label>
            <div className="grid grid-cols-2 gap-3">
              {DIETARY_RESTRICTIONS.map(restriction => (
                <div key={restriction} className="flex items-center space-x-2">
                  <Checkbox
                    id={restriction}
                    checked={formData.dietary_restrictions?.includes(restriction) || false}
                    onCheckedChange={() => handleDietaryRestrictionToggle(restriction)}
                  />
                  <Label htmlFor={restriction} className="font-normal cursor-pointer">
                    {restriction}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Medical Conditions */}
          <div className="space-y-2">
            <Label htmlFor="conditions">Medical Conditions (optional)</Label>
            <Textarea
              id="conditions"
              placeholder="Any health conditions we should know about? e.g., Back pain, diabetes, asthma..."
              value={formData.medical_conditions}
              onChange={e => handleInputChange('medical_conditions', e.target.value)}
              rows={3}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-lg">
              <AlertCircle className="w-4 h-4" />
              <p className="text-sm">{error}</p>
            </div>
          )}
        </div>

        <div className="flex gap-3">
          <Button
            onClick={handleSubmit}
            disabled={loading}
            className="flex-1"
          >
            {loading ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                Setting up profile...
              </>
            ) : (
              'Complete Setup'
            )}
          </Button>
        </div>
      </AlertDialogContent>
    </AlertDialog>
  );
}
