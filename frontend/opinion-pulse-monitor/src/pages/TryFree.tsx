
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, TrendingUp, TrendingDown, Minus, Upload, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import axios from 'axios';

const TryFreePage = () => {
  const [text, setText] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'text/plain') {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target.result;
        if (typeof result === 'string') {
          setText(result);
          setUploadedFile(file);
        }
      };
      reader.readAsText(file);
    } else {
      alert('Please upload a text file (.txt)');
    }
  };

  const analyzeSentiment = async () => {
    if (!text.trim()) return;
    setIsAnalyzing(true);
    setAnalysis(null);

    try {
      // Step 1: Analyze the sentiment using FastAPI
      const res = await axios.post('http://127.0.0.1:8000/analyze', { text });
      const result = res.data;
      setAnalysis(result);

      // Step 2: Save the result in MongoDB
      await axios.post("http://127.0.0.1:8000/api/submit-review", {
        text: text,
        sentiment: result.sentiment,
        score: result.score,
        confidence: result.confidence
      });
    } catch (error) {
      console.error('Error connecting to FastAPI:', error);
      alert("Failed to analyze or save. Please check if your backend is running.");
    }

    setIsAnalyzing(false);
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'Positive':
        return <TrendingUp className="w-5 h-5 text-green-500" />;
      case 'Negative':
        return <TrendingDown className="w-5 h-5 text-red-500" />;
      default:
        return <Minus className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getSentimentColor = (sentiment) => {
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
              Test our AI-powered sentiment analysis with your own text. Enter any customer review, feedback, or comment below, or upload a text file.
            </p>
          </div>

          {/* Analysis Form */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm mb-8">
            <CardHeader>
              <CardTitle>Enter Text for Analysis</CardTitle>
              <CardDescription>
                Paste any customer review, feedback, or text you'd like to analyze, or upload a text file
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* File Upload Section */}
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
                <input
                  type="file"
                  accept=".txt"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="flex flex-col items-center gap-3">
                    <div className="p-3 bg-blue-100 rounded-full">
                      <Upload className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-lg font-medium text-gray-700">Upload a text file</p>
                      <p className="text-sm text-gray-500">Click to browse or drag and drop (.txt files only)</p>
                    </div>
                  </div>
                </label>
                {uploadedFile && (
                  <div className="mt-4 flex items-center justify-center gap-2 text-green-600">
                    <FileText className="w-4 h-4" />
                    <span className="text-sm font-medium">{uploadedFile.name} uploaded</span>
                  </div>
                )}
              </div>

              <div className="text-center text-gray-500 font-medium">OR</div>

              {/* Text Input */}
              <Textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Example: This product is amazing! The quality exceeded my expectations and the customer service was fantastic."
                className="min-h-32 resize-none"
              />
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">
                  {text.length}/1000 characters
                </span>
                <Button
                  onClick={analyzeSentiment}
                  disabled={!text.trim() || isAnalyzing}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isAnalyzing ? 'Analyzing...' : 'Analyze Sentiment'}
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
