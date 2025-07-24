
import React from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { MessageSquare, Users, Target, Award } from 'lucide-react';

const About = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <Navbar />
      
      <div className="container mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center max-w-4xl mx-auto mb-16">
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-blue-600 rounded-full">
              <MessageSquare className="w-10 h-10 text-white" />
            </div>
          </div>
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            About SentimentScope
          </h1>
          <p className="text-xl text-gray-600 leading-relaxed">
            We're revolutionizing how businesses understand their customers through 
            advanced AI-powered sentiment analysis and actionable insights.
          </p>
        </div>

        {/* Mission Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-8 shadow-lg">
            <div className="flex items-center gap-3 mb-4">
              <Target className="w-8 h-8 text-blue-600" />
              <h2 className="text-2xl font-bold">Our Mission</h2>
            </div>
            <p className="text-gray-600 leading-relaxed">
              To empower businesses with deep customer insights through cutting-edge sentiment analysis, 
              helping them make data-driven decisions that improve customer satisfaction and drive growth.
            </p>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-8 shadow-lg">
            <div className="flex items-center gap-3 mb-4">
              <Award className="w-8 h-8 text-blue-600" />
              <h2 className="text-2xl font-bold">Our Vision</h2>
            </div>
            <p className="text-gray-600 leading-relaxed">
              To become the leading platform for sentiment analysis, making customer feedback 
              analysis accessible and actionable for businesses of all sizes worldwide.
            </p>
          </div>
        </div>

        {/* Team Section */}
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <div className="p-3 bg-purple-600 rounded-full">
              <Users className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold mb-8">Our Story</h2>
          <div className="max-w-4xl mx-auto bg-white/80 backdrop-blur-sm rounded-xl p-8 shadow-lg">
            <p className="text-gray-600 leading-relaxed mb-6">
              Founded in 2023, SentimentScope emerged from a simple observation: businesses were drowning 
              in customer feedback but struggling to extract meaningful insights from it. Our team of AI 
              researchers and business analysts came together to solve this challenge.
            </p>
            <p className="text-gray-600 leading-relaxed">
              Today, we're proud to serve over 5,000 businesses worldwide, helping them understand their 
              customers better through advanced sentiment analysis, real-time monitoring, and actionable 
              business insights.
            </p>
          </div>
        </div>

        {/* Values Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center p-6 bg-white/60 backdrop-blur-sm rounded-xl">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Innovation</h3>
            <p className="text-gray-600">
              Continuously pushing the boundaries of AI and machine learning to deliver 
              the most accurate sentiment analysis.
            </p>
          </div>

          <div className="text-center p-6 bg-white/60 backdrop-blur-sm rounded-xl">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Customer Focus</h3>
            <p className="text-gray-600">
              Every feature we build is designed with our customers' success in mind, 
              ensuring maximum value and usability.
            </p>
          </div>

          <div className="text-center p-6 bg-white/60 backdrop-blur-sm rounded-xl">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Award className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Excellence</h3>
            <p className="text-gray-600">
              We maintain the highest standards in everything we do, from our technology 
              to our customer service.
            </p>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default About;
