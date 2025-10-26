import React from 'react';
import Lottie from 'lottie-react';

interface LottieLoaderProps {
  size?: number;
  text?: string;
}

const LottieLoader: React.FC<LottieLoaderProps> = ({ size = 100, text }) => {
  const [animationData, setAnimationData] = React.useState<any>(null);

  React.useEffect(() => {
    fetch('/glow-loading.json')
      .then(response => response.json())
      .then(data => setAnimationData(data))
      .catch(error => console.error('Error loading animation:', error));
  }, []);

  if (!animationData) {
    return (
      <div className="flex flex-col items-center justify-center gap-2">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        {text && <p className="text-sm text-muted-foreground">{text}</p>}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center gap-2">
      <Lottie 
        animationData={animationData} 
        loop={true}
        style={{ width: size, height: size }}
      />
      {text && <p className="text-sm text-muted-foreground animate-pulse">{text}</p>}
    </div>
  );
};

export default LottieLoader;
