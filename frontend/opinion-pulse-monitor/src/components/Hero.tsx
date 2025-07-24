
import React from 'react';
import { Button } from '@/components/ui/button';
import { BarChart, TrendingUp, MessageSquare } from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel"
import Autoplay from "embla-carousel-autoplay"

const Hero = () => {
  const carouselImages = [
    {
      src: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
      alt: "Data charts and graphs"
    },
    {
      src: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
      alt: "Business intelligence dashboard"
    },
    {
      src: "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
      alt: "Market research and analytics"
    },
    {
      src: "https://images.unsplash.com/photo-1557804506-669a67965ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
      alt: "Customer feedback analysis"
    },{
      src: "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80", 
      alt: "Data visualization on laptop"
    },
    {
      src: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
      alt: "Professional working with analytics"
    },
    {
      src: "https://images.unsplash.com/photo-1605810230434-7631ac76ec81?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
      alt: "Data screens and analytics"
    },
    
  ];

  const plugin = React.useRef(
    Autoplay({ delay: 3000, stopOnInteraction: true })
  );

  return (
    <section className="relative overflow-hidden bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 text-white">
      <div className="absolute inset-0 bg-black/20"></div>
      <div className="relative container mx-auto px-6 py-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center max-w-7xl mx-auto">
          {/* Left side - Content */}
          <div className="text-center lg:text-left">
            <div className="flex justify-center lg:justify-start items-center gap-4 mb-8">
              <div className="p-3 bg-white/20 rounded-full backdrop-blur-sm">
                <MessageSquare className="w-8 h-8" />
              </div>
              <div className="p-3 bg-white/20 rounded-full backdrop-blur-sm">
                <BarChart className="w-8 h-8" />
              </div>
              <div className="p-3 bg-white/20 rounded-full backdrop-blur-sm">
                <TrendingUp className="w-8 h-8" />
              </div>
            </div>
            
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
              SentimentScope
            </h1>
            
            <p className="text-lg md:text-xl mb-8 text-blue-100 leading-relaxed">
              Unlock the power of customer feedback with AI-driven sentiment analysis. 
              Transform reviews into actionable business insights.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start items-center mb-12">
              <Link to="/dashboard">
                <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50 px-8 py-4 text-lg font-semibold rounded-full shadow-lg hover:shadow-xl transition-all duration-300">
                  View Dashboard
                </Button>
              </Link>
              <Link to="/try-free">
                <Button size="lg" variant="outline" className="bg-white text-blue-600 hover:bg-blue-50 px-8 py-4 text-lg font-semibold rounded-full shadow-lg hover:shadow-xl transition-all duration-300">
                  Try Free Analysis
                </Button>
              </Link>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div className="p-6 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                <div className="text-3xl font-bold mb-2">98.5%</div>
                <div className="text-blue-200">Accuracy Rate</div>
              </div>
              <div className="p-6 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                <div className="text-3xl font-bold mb-2">10M+</div>
                <div className="text-blue-200">Reviews Analyzed</div>
              </div>
              <div className="p-6 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                <div className="text-3xl font-bold mb-2">5000+</div>
                <div className="text-blue-200">Happy Businesses</div>
              </div>
            </div>
          </div>

          {/* Right side - Carousel */}
          <div className="relative">
            <Carousel 
              className="w-full max-w-lg mx-auto"
              plugins={[plugin.current]}
              onMouseEnter={plugin.current.stop}
              onMouseLeave={plugin.current.reset}
            >
              <CarouselContent>
                {carouselImages.map((image, index) => (
                  <CarouselItem key={index}>
                    <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                      <img
                        src={image.src}
                        alt={image.alt}
                        className="w-full h-80 md:h-96 object-cover"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent"></div>
                    </div>
                  </CarouselItem>
                ))}
              </CarouselContent>
              <CarouselPrevious className="left-4 bg-white/20 border-white/30 text-white hover:bg-white/30" />
              <CarouselNext className="right-4 bg-white/20 border-white/30 text-white hover:bg-white/30" />
            </Carousel>
            
            {/* Floating elements for visual appeal */}
            <div className="absolute -top-4 -right-4 w-16 h-16 bg-white/10 rounded-full backdrop-blur-sm animate-pulse"></div>
            <div className="absolute -bottom-4 -left-4 w-12 h-12 bg-blue-400/20 rounded-full backdrop-blur-sm animate-pulse delay-1000"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
