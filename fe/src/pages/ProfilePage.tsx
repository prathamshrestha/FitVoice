import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, Edit2, LogOut, Loader, Check } from 'lucide-react';
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface UserProfile {
  user_id: string;
  name: string;
  age?: number;
  fitness_level?: string;
  primary_goal: string;
  weight_kg?: number;
  height_cm?: number;
  medical_conditions?: string;
  dietary_restrictions?: string[];
  created_at?: string;
  updated_at?: string;
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

export default function ProfilePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [formData, setFormData] = useState<UserProfile | null>(null);

  const userId = localStorage.getItem('user_id');

  useEffect(() => {
    if (!userId) {
      navigate('/');
      return;
    }
    fetchProfile();
  }, [userId, navigate]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await fetch(`http://localhost:8000/api/users/${userId}`);
      
      if (!response.ok) {
        throw new Error('Profile not found');
      }

      const data = await response.json();
      setProfile(data);
      setFormData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof UserProfile, value: any) => {
    setFormData(prev => prev ? {
      ...prev,
      [field]: value
    } : null);
  };

  const handleDietaryRestrictionToggle = (restriction: string) => {
    if (!formData) return;
    setFormData(prev => prev ? {
      ...prev,
      dietary_restrictions: prev.dietary_restrictions?.includes(restriction)
        ? prev.dietary_restrictions.filter(r => r !== restriction)
        : [...(prev.dietary_restrictions || []), restriction]
    } : null);
  };

  const handleSave = async () => {
    if (!formData) return;

    try {
      setSaving(true);
      setError('');
      setSuccess('');

      const response = await fetch(`http://localhost:8000/api/users/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
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
        throw new Error(errorData.error || 'Failed to save profile');
      }

      const updatedProfile = await response.json();
      setProfile(updatedProfile.profile);
      setFormData(updatedProfile.profile);
      setIsEditing(false);
      setSuccess('Profile updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user_id');
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background pt-16 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!profile || !formData) {
    return (
      <div className="min-h-screen bg-background pt-16 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <AlertCircle className="w-8 h-8 text-destructive mx-auto mb-2" />
            <CardTitle>Profile Not Found</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">{error || 'Your profile could not be loaded.'}</p>
            <Button onClick={() => navigate('/')} className="w-full">
              Go Back Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pt-16 pb-10">
      <div className="max-w-4xl mx-auto px-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">My Profile</h1>
            <p className="text-muted-foreground mt-1">Manage your fitness profile and preferences</p>
          </div>
          <div className="flex gap-2">
            {!isEditing && (
              <Button
                variant="outline"
                onClick={() => setIsEditing(true)}
                className="gap-2"
              >
                <Edit2 className="w-4 h-4" />
                Edit Profile
              </Button>
            )}
            <Button
              variant="outline"
              onClick={handleLogout}
              className="gap-2 text-destructive hover:text-destructive"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
          </div>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="flex items-center gap-2 p-4 bg-green-500/10 text-green-700 rounded-lg mb-6">
            <Check className="w-4 h-4" />
            <p>{success}</p>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 p-4 bg-destructive/10 text-destructive rounded-lg mb-6">
            <AlertCircle className="w-4 h-4" />
            <p>{error}</p>
          </div>
        )}

        {/* Profile Card */}
        <Card>
          <CardHeader>
            <CardTitle>Profile Information</CardTitle>
            <CardDescription>
              {!isEditing && `Last updated: ${new Date(profile.updated_at || '').toLocaleDateString()}`}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              {isEditing ? (
                <Input
                  id="name"
                  value={formData.name}
                  onChange={e => handleInputChange('name', e.target.value)}
                />
              ) : (
                <p className="font-medium">{profile.name}</p>
              )}
            </div>

            {/* Age and Weight/Height */}
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="age">Age</Label>
                {isEditing ? (
                  <Input
                    id="age"
                    type="number"
                    value={formData.age || ''}
                    onChange={e => handleInputChange('age', e.target.value ? parseInt(e.target.value) : undefined)}
                  />
                ) : (
                  <p className="font-medium text-muted-foreground">{profile.age || '-'}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="weight">Weight (kg)</Label>
                {isEditing ? (
                  <Input
                    id="weight"
                    type="number"
                    step="0.1"
                    value={formData.weight_kg || ''}
                    onChange={e => handleInputChange('weight_kg', e.target.value ? parseFloat(e.target.value) : undefined)}
                  />
                ) : (
                  <p className="font-medium text-muted-foreground">{profile.weight_kg ? `${profile.weight_kg}kg` : '-'}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="height">Height (cm)</Label>
                {isEditing ? (
                  <Input
                    id="height"
                    type="number"
                    value={formData.height_cm || ''}
                    onChange={e => handleInputChange('height_cm', e.target.value ? parseFloat(e.target.value) : undefined)}
                  />
                ) : (
                  <p className="font-medium text-muted-foreground">{profile.height_cm ? `${profile.height_cm}cm` : '-'}</p>
                )}
              </div>
            </div>

            {/* Fitness Level */}
            <div className="space-y-2">
              <Label htmlFor="fitness-level">Fitness Level</Label>
              {isEditing ? (
                <Select value={formData.fitness_level || 'beginner'} onValueChange={v => handleInputChange('fitness_level', v)}>
                  <SelectTrigger>
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
              ) : (
                <p className="font-medium text-muted-foreground">
                  {FITNESS_LEVELS.find(l => l.value === profile.fitness_level)?.label || '-'}
                </p>
              )}
            </div>

            {/* Primary Goal */}
            <div className="space-y-2">
              <Label htmlFor="goal">Primary Fitness Goal</Label>
              {isEditing ? (
                <Select value={formData.primary_goal} onValueChange={v => handleInputChange('primary_goal', v)}>
                  <SelectTrigger>
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
              ) : (
                <p className="font-medium text-muted-foreground">
                  {FITNESS_GOALS.find(g => g.value === profile.primary_goal)?.label}
                </p>
              )}
            </div>

            {/* Dietary Restrictions */}
            <div className="space-y-3">
              <Label>Dietary Restrictions</Label>
              {isEditing ? (
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
              ) : (
                <div>
                  {profile.dietary_restrictions && profile.dietary_restrictions.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {profile.dietary_restrictions.map(restriction => (
                        <span key={restriction} className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm">
                          {restriction}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No dietary restrictions specified</p>
                  )}
                </div>
              )}
            </div>

            {/* Medical Conditions */}
            <div className="space-y-2">
              <Label htmlFor="conditions">Medical Conditions</Label>
              {isEditing ? (
                <Textarea
                  id="conditions"
                  value={formData.medical_conditions || ''}
                  onChange={e => handleInputChange('medical_conditions', e.target.value)}
                  rows={3}
                />
              ) : (
                <p className="text-muted-foreground whitespace-pre-wrap">
                  {profile.medical_conditions || 'No medical conditions specified'}
                </p>
              )}
            </div>

            {/* Action Buttons */}
            {isEditing && (
              <div className="flex gap-3 pt-4 border-t">
                <Button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex-1"
                >
                  {saving ? (
                    <>
                      <Loader className="w-4 h-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsEditing(false);
                    setFormData(profile);
                  }}
                  disabled={saving}
                >
                  Cancel
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
