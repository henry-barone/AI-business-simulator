
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ExternalLink } from 'lucide-react';

const AboutUs = () => {
  return (
    <div className="container mx-auto px-6 py-16 space-y-16">
      {/* Header */}
      <Card className="professional-card">
        <CardContent className="p-16 text-center">
          <h1 className="text-6xl font-bold professional-heading mb-8">About SPAIK</h1>
          <p className="text-xl professional-text max-w-4xl mx-auto">
            Pioneering the future of business optimization through AI-powered digital twins
          </p>
        </CardContent>
      </Card>

      {/* Company Description */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="text-4xl professional-heading">Our Story</CardTitle>
        </CardHeader>
        <CardContent className="p-12">
          <div className="professional-text text-lg leading-relaxed space-y-8">
            <p>
              SPAIK is an innovative AI-consulting startup based in the vibrant tech hub of Amsterdam, Netherlands. 
              We specialize in creating comprehensive digital twins for businesses across various industries, 
              enabling them to simulate, analyze, and optimize their operations with unprecedented precision.
            </p>
            <p>
              Our mission is to empower businesses through AI-driven optimization, transforming complex data 
              into actionable insights that drive measurable growth and operational efficiency. We believe 
              that every business deserves access to cutting-edge AI technology that was once only available 
              to large corporations.
            </p>
            <p>
              Our core services include digital twin development, process automation consulting, 
              predictive analytics implementation, and ROI optimization strategies. We work closely 
              with our clients to understand their unique challenges and deliver tailored solutions 
              that produce tangible results.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* External Link */}
      <Card className="professional-card">
        <CardContent className="p-12 text-center">
          <h2 className="text-3xl professional-heading mb-6">Learn More About Our Work</h2>
          <p className="professional-text mb-8 text-lg">
            Visit our main website to explore our full range of services and see our latest projects.
          </p>
          <a 
            href="https://www.spaik.io/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center"
          >
            <Button className="professional-button text-lg px-8 py-4">
              Visit Our Main Website
              <ExternalLink className="ml-2 w-5 h-5" />
            </Button>
          </a>
        </CardContent>
      </Card>

      {/* Leadership & CTA */}
      <Card className="professional-card">
        <CardContent className="p-12">
          <div className="grid md:grid-cols-2 gap-12">
            <div>
              <h2 className="text-4xl professional-heading mb-6">Our Leadership</h2>
              <p className="professional-text mb-6 text-lg">
                Our team consists of experienced AI specialists, business consultants, and technology 
                experts who are passionate about helping businesses thrive in the digital age.
              </p>
              <p className="professional-text text-lg">
                With decades of combined experience in artificial intelligence, machine learning, 
                and business optimization, our founders have helped companies across Europe 
                achieve remarkable transformations.
              </p>
            </div>
            <div className="bg-gradient-to-br from-purple-600 to-blue-600 p-10 rounded-lg text-center text-white">
              <h3 className="text-3xl font-bold mb-6">Ready to Transform Your Business?</h3>
              <p className="mb-8 opacity-90 text-lg">
                Schedule a personal consultation with our CEO to discuss your specific challenges 
                and how SPAIK can help you achieve your goals.
              </p>
              <Button className="bg-white text-purple-600 hover:bg-gray-100 px-8 py-4 text-lg font-semibold rounded-lg">
                Book a Call with Our CEO Today
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AboutUs;
