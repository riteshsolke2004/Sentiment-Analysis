
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const SentimentAnalyzer = () => {
  const [review, setReview] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const analyzeReview = async () => {
    if (!review.trim()) return;
    
    setIsAnalyzing(true);
    
    // Simulate API call with mock sentiment analysis
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Simple sentiment analysis simulation
    const positiveWords = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'fantastic', 'wonderful', 'perfect', 'awesome'];
    const negativeWords = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting', 'disappointing', 'useless'];
    
    const lowerReview = review.toLowerCase();
    const positiveCount = positiveWords.filter(word => lowerReview.includes(word)).length;
    const negativeCount = negativeWords.filter(word => lowerReview.includes(word)).length;
    
    let sentiment, confidence, color, icon;
    
    if (positiveCount > negativeCount) {
      sentiment = 'Positive';
      confidence = Math.min(85 + positiveCount * 5, 95);
      color = 'bg-green-500';
      icon = TrendingUp;
    } else if (negativeCount > positiveCount) {
      sentiment = 'Negative';
      confidence = Math.min(80 + negativeCount * 5, 95);
      color = 'bg-red-500';
      icon = TrendingDown;
    } else {
      sentiment = 'Neutral';
      confidence = Math.floor(Math.random() * 20) + 70;
      color = 'bg-yellow-500';
      icon = Minus;
    }
    
    setAnalysis({
      sentiment,
      confidence,
      color,
      icon,
      keywords: sentiment === 'Positive' ? positiveWords.filter(word => lowerReview.includes(word)) :
                sentiment === 'Negative' ? negativeWords.filter(word => lowerReview.includes(word)) :
                ['neutral', 'average', 'okay']
    });
    
    setIsAnalyzing(false);
  };

  const IconComponent = analysis?.icon;

  return (
    <section className="py-20 px-6">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Real-Time Sentiment Analysis
          </h2>
          <p className="text-xl text-gray-600">
            Paste any product review and get instant sentiment insights
          </p>
        </div>
        
        <Card className="shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="w-6 h-6 text-blue-500" />
              Analyze Customer Review
            </CardTitle>
            <CardDescription>
              Enter a product review to analyze its sentiment and extract key insights
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <Textarea
                placeholder="Paste your product review here... For example: 'This product is absolutely amazing! The quality exceeded my expectations and the customer service was fantastic. I would definitely recommend it to others.'"
                className="min-h-32 text-lg border-2 focus:border-blue-500 transition-colors"
                value={review}
                onChange={(e) => setReview(e.target.value)}
              />
            </div>
            
            <Button 
              onClick={analyzeReview}
              disabled={!review.trim() || isAnalyzing}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white py-3 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Sentiment'}
            </Button>
            
            {analysis && (
              <div className="mt-8 p-6 bg-gradient-to-r from-slate-50 to-blue-50 rounded-xl border border-blue-200">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-full ${analysis.color}`}>
                      {IconComponent && <IconComponent className="w-6 h-6 text-white" />}
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-gray-800">{analysis.sentiment}</h3>
                      <p className="text-gray-600">Confidence: {analysis.confidence}%</p>
                    </div>
                  </div>
                  <div className="w-24 h-24 relative">
                    <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
                      <path
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke="#e5e7eb"
                        strokeWidth="2"
                      />
                      <path
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke={analysis.color.replace('bg-', '#').replace('500', '500')}
                        strokeWidth="2"
                        strokeDasharray={`${analysis.confidence}, 100`}
                        className="transition-all duration-1000 ease-out"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-bold text-gray-700">{analysis.confidence}%</span>
                    </div>
                  </div>
                </div>
                
                {analysis.keywords.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-3 text-gray-700">Key Sentiment Indicators:</h4>
                    <div className="flex flex-wrap gap-2">
                      {analysis.keywords.map((keyword, index) => (
                        <Badge key={index} variant="secondary" className="px-3 py-1 bg-white border border-gray-300">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default SentimentAnalyzer;
