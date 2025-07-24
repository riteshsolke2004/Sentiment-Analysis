import React, { useEffect, useState } from 'react';
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, TrendingUp, Users } from 'lucide-react';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';


interface Review {
  id: string;
  text: string;
  sentiment: 'Positive' | 'Neutral' | 'Negative';
  score: number;
}

const DashboardPage: React.FC = () => {
  const [recentReviews, setRecentReviews] = useState<Review[]>([]);

  // Fetch reviews from backend
  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const res = await fetch('http://localhost:8000/get-reviews');
        const data = await res.json();
        setRecentReviews(data);
      } catch (error) {
        console.error('Failed to fetch reviews:', error);
      }
    };

    fetchReviews();
  }, []);

  const sentimentTrend = [
    { month: 'Jan', positive: 65, negative: 20, neutral: 15 },
    { month: 'Feb', positive: 72, negative: 18, neutral: 10 },
    { month: 'Mar', positive: 68, negative: 22, neutral: 10 },
    { month: 'Apr', positive: 75, negative: 15, neutral: 10 },
    { month: 'May', positive: 82, negative: 12, neutral: 6 },
    { month: 'Jun', positive: 78, negative: 14, neutral: 8 }
  ];

  const reviewVolume = [
    { day: 'Mon', reviews: 145 },
    { day: 'Tue', reviews: 162 },
    { day: 'Wed', reviews: 134 },
    { day: 'Thu', reviews: 178 },
    { day: 'Fri', reviews: 195 },
    { day: 'Sat', reviews: 156 },
    { day: 'Sun', reviews: 123 }
  ];

  const sentimentDistribution = [
    { name: 'Positive', value: 78, color: '#10b981' },
    { name: 'Neutral', value: 14, color: '#f59e0b' },
    { name: 'Negative', value: 8, color: '#ef4444' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">

      <div className="container mx-auto px-6 py-8">
        {/* Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm font-medium">Positive Reviews</p>
                  <p className="text-3xl font-bold">78%</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-200" />
              </div>
              <div className="flex items-center mt-2">
                <span className="text-green-200 text-sm">↗ 5.2% from last month</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm font-medium">Total Reviews</p>
                  <p className="text-3xl font-bold">24.7K</p>
                </div>
                <MessageSquare className="w-8 h-8 text-blue-200" />
              </div>
              <div className="flex items-center mt-2">
                <span className="text-blue-200 text-sm">↗ 12.3% from last month</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm font-medium">Avg. Sentiment</p>
                  <p className="text-3xl font-bold">8.2/10</p>
                </div>
                <Users className="w-8 h-8 text-purple-200" />
              </div>
              <div className="flex items-center mt-2">
                <span className="text-purple-200 text-sm">↗ 0.7 from last month</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100 text-sm font-medium">Response Rate</p>
                  <p className="text-3xl font-bold">94%</p>
                </div>
                <TrendingUp className="w-8 h-8 text-orange-200" />
              </div>
              <div className="flex items-center mt-2">
                <span className="text-orange-200 text-sm">↗ 2.1% from last month</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Sentiment Trends Over Time</CardTitle>
              <CardDescription>Monthly breakdown of sentiment analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={sentimentTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="positive" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
                  <Area type="monotone" dataKey="neutral" stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.6} />
                  <Area type="monotone" dataKey="negative" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.6} />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Review Volume</CardTitle>
              <CardDescription>Daily review count for the past week</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={reviewVolume}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="reviews" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Pie Chart + Real Reviews */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Sentiment Distribution</CardTitle>
              <CardDescription>Current sentiment breakdown</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={sentimentDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {sentimentDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 mt-4">
                {sentimentDistribution.map((item, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                    <span className="text-sm text-gray-600">{item.name} {item.value}%</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2 shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Recent Reviews</CardTitle>
              <CardDescription>Latest customer feedback analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentReviews.map((review) => (
                  <div key={review.id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex items-start justify-between mb-2">
                      <p className="text-gray-800 flex-1 mr-4">{review.text}</p>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <Badge
                          variant={review.sentiment === 'Positive' ? 'default' : review.sentiment === 'Negative' ? 'destructive' : 'secondary'}
                          className={review.sentiment === 'Positive' ? 'bg-green-500' : ''}
                        >
                          {review.sentiment}
                        </Badge>
                        <span className="text-sm font-medium text-gray-600">{review.score}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

    </div>
  );
};

export default DashboardPage;
