import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, TrendingUp, TrendingDown, Minus, Link2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import axios from 'axios';

// Define a type for the analysis result for better type-checking
interface AnalysisResult {
  sentiment: 'Positive' | 'Negative' | 'Neutral';
  score: number;
  confidence: number;
  keywords: string[];
}

// Define a type for a single scraped review
interface ScrapedReview {
  review_text: string;
  // Add other fields like rating, title, etc., if you need them
}

const TryFreePage = () => {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');

  const analyzeSentiment = async () => {
    if (!url.trim() && !text.trim()) return;

    setIsLoading(true);
    setAnalysis(null);

    let textToAnalyze = text;

    try {
      // --- STEP 1: Scrape reviews if a URL is provided ---
      if (url.trim()) {
        setLoadingMessage('Scraping Reviews...');
        console.log('Scraping URL:', url);

        // Call your new scraping endpoint
        const scrapeRes = await axios.post<{ reviews: ScrapedReview[] }>('http://127.0.0.1:8000/scrape', { url });
        
        // Combine all review texts into a single block of text
        const scrapedText = scrapeRes.data.reviews
          .map(review => review.review_text)
          .filter(Boolean) // Filter out any null or empty reviews
          .join('\n\n---\n\n');

        if (!scrapedText) {
          throw new Error("Could not extract any review text from the URL.");
        }

        setText(scrapedText); // Update the text area with scraped content
        textToAnalyze = scrapedText;
      }

      // --- STEP 2: Analyze the sentiment of the text ---
      setLoadingMessage('Analyzing Sentiment...');
      console.log('Analyzing text...');
      
      const analysisRes = await axios.post('http://127.0.0.1:8000/analyze', { text: textToAnalyze });
      const result = analysisRes.data;
      setAnalysis(result);

      // --- STEP 3: Save the result in MongoDB ---
      await axios.post("http://127.0.0.1:8000/api/submit-review", {
        text: textToAnalyze,
        sentiment: result.sentiment,
        score: result.score,
        confidence: result.confidence
      });

    } catch (error) {
      console.error('An error occurred:', error);
      alert("Failed to process the request. Please check if your backend is running and the URL is correct.");
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const getSentimentIcon = (sentiment: AnalysisResult['sentiment']) => {
    switch (sentiment) {
      case 'Positive':
        return <TrendingUp className="w-5 h-5 text-green-500" />;
      case 'Negative':
        return <TrendingDown className="w-5 h-5 text-red-500" />;
      default:
        return <Minus className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getSentimentColor = (sentiment: AnalysisResult['sentiment']) => {
    switch (sentiment) {
      case 'Positive':
        return 'bg-green-500';
      case 'Negative':
        return 'bg-red-500';
      default:
        return 'bg-yellow-500';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <Navbar />

      <div className="container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="p-3 bg-blue-600 rounded-full">
                <MessageSquare className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Try Free Analysis
              </h1>
            </div>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Test our AI-powered sentiment analysis. Enter any customer review, feedback, or paste a Flipkart product URL to scrape and analyze reviews.
            </p>
          </div>

          {/* Analysis Form */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm mb-8">
            <CardHeader>
              <CardTitle>Enter Content for Analysis</CardTitle>
              <CardDescription>
                Paste a Flipkart URL to scrape reviews, or enter text directly.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* URL Input Section */}
              <div>
                <label htmlFor="url-input" className="text-sm font-medium text-gray-700">Analyze from URL</label>
                <div className="relative mt-1">
                  <Link2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    id="url-input"
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://www.flipkart.com/your-product/p/..."
                    className="pl-10"
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div className="text-center text-gray-500 font-medium">OR</div>

              {/* Text Input */}
              <Textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Example: This product is amazing! The quality exceeded my expectations and the customer service was fantastic."
                className="min-h-32 resize-none"
                disabled={isLoading}
              />
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">
                  {text.length} characters
                </span>
                <Button
                  onClick={analyzeSentiment}
                  disabled={(!text.trim() && !url.trim()) || isLoading}
                  className="bg-blue-600 hover:bg-blue-700 w-48"
                >
                  {isLoading ? loadingMessage : 'Analyze Sentiment'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Analysis Results */}
          {analysis && (
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  {getSentimentIcon(analysis.sentiment)}
                  Analysis Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div className="text-center p-6 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-center mb-3">
                      <Badge className={`${getSentimentColor(analysis.sentiment)} text-white`}>
                        {analysis.sentiment}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">Sentiment</p>
                  </div>

                  <div className="text-center p-6 bg-gray-50 rounded-lg">
                    <div className="text-3xl font-bold text-blue-600 mb-2">
                      {analysis.score}%
                    </div>
                    <p className="text-sm text-gray-600">Sentiment Score</p>
                  </div>

                  <div className="text-center p-6 bg-gray-50 rounded-lg">
                    <div className="text-3xl font-bold text-green-600 mb-2">
                      {analysis.confidence.toFixed(1)}%
                    </div>
                    <p className="text-sm text-gray-600">Confidence</p>
                  </div>
                </div>

                {analysis.keywords?.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-3">Key Sentiment Words Detected:</h4>
                    <div className="flex flex-wrap gap-2">
                      {analysis.keywords.map((keyword, index) => (
                        <Badge key={index} variant="outline">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* CTA */}
          <div className="text-center mt-12 p-8 bg-white/60 backdrop-blur-sm rounded-xl border border-white/20">
            <h3 className="text-2xl font-bold mb-4">Ready for More Advanced Analysis?</h3>
            <p className="text-gray-600 mb-6">
              Get detailed insights, batch processing, and real-time monitoring with our full platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/dashboard">
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
                  View Dashboard
                </Button>
              </Link>
              <Link to="/">
                <Button size="lg" variant="outline">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default TryFreePage;