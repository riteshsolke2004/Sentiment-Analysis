
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, TrendingUp, MessageSquare, Search, Star, Check } from 'lucide-react';

const Features = () => {
  const features = [
    {
      icon: MessageSquare,
      title: 'Real-Time Analysis',
      description: 'Get instant sentiment analysis results with our advanced AI algorithms.',
      color: 'bg-blue-500'
    },
    {
      icon: BarChart,
      title: 'Visual Analytics',
      description: 'Beautiful charts and graphs to visualize sentiment trends over time.',
      color: 'bg-purple-500'
    },
    {
      icon: TrendingUp,
      title: 'Trend Monitoring',
      description: 'Track sentiment changes and identify patterns in customer feedback.',
      color: 'bg-green-500'
    },
    {
      icon: Search,
      title: 'Keyword Extraction',
      description: 'Automatically identify key terms and phrases that drive sentiment.',
      color: 'bg-orange-500'
    },
    {
      icon: Star,
      title: 'Review Scoring',
      description: 'Convert qualitative feedback into quantitative sentiment scores.',
      color: 'bg-pink-500'
    },
    {
      icon: Check,
      title: 'Bulk Processing',
      description: 'Analyze thousands of reviews simultaneously for comprehensive insights.',
      color: 'bg-indigo-500'
    }
  ];

  return (
    <section className="py-20 px-6 bg-white">
      <div className="container mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
            Powerful Features for Better Insights
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Everything you need to understand your customers' sentiment and make data-driven decisions
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const IconComponent = feature.icon;
            return (
              <Card key={index} className="group hover:shadow-2xl transition-all duration-300 border-0 bg-gradient-to-br from-white to-gray-50 hover:scale-105">
                <CardHeader className="text-center pb-4">
                  <div className={`w-16 h-16 mx-auto rounded-2xl ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <IconComponent className="w-8 h-8 text-white" />
                  </div>
                  <CardTitle className="text-xl font-bold text-gray-800">
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-center text-gray-600 text-base leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Features;
