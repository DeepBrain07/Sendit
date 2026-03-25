import { Button } from "../../components/Button";
import { useState, useEffect } from "react";
import { logo2, selfie2 } from "../../assets/images";
import { useNavigate } from "react-router-dom";
import { Icon } from "@iconify/react/dist/iconify.js";
import confetti from "canvas-confetti";

export const Step4 = ({ amount, isFragile, offerType, offerImage, isUrgent, from, to, receiverName, receiverContact }: { amount: string; isFragile: boolean | null; offerType: string; offerImage: File | null; isUrgent: boolean; from: string; to: string; receiverName: string; receiverContact: string }) => {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const navigate = useNavigate();

  const handlePostOffer = () => {
    // Fire confetti immediately
    confetti({
      particleCount: 150,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#1D4ED8', '#60A5FA', '#FFFFFF']
    });
    // Toggle to success view
    setIsSubmitted(true);
  };

  if (isSubmitted) {
    return (
      <div>
        <div className="w-full flex mt-4 flex-col justify-center items-center gap-8 px-4">
          <img src={logo2} alt="Sendit Logo" className="size-32 my-[-20px] mt-[-60px]" />

          <div className="flex flex-col justify-center items-center gap-2">
            {/* Using an icon or generic image since selfie2 might be specific to user verification */}
            <div className="bg-primary/10 p-6 rounded-full mb-4">
                <Icon icon="icon-park-solid:check-one" className="text-primary text-6xl" />
            </div>
            <h2 className="text-center text-xl font-bold mb-2">Offer Posted Successfully!</h2>
            <p className="text-center text-gray-500 text-sm mb-8">
              Your delivery offer from <b>{from}</b> to <b>{to}</b> is now live. <br /> 
              Travelers will notify you when they are interested.
            </p>
          </div>
          <Button title="Proceed to Homepage" onClick={() => navigate('/home')} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 !text-black">
      <div className="flex flex-col">
        <h2>Review & confirm</h2>
        <p className="!text-bodyText/50 !font-bold !text-sm">Check everything is correct before posting.</p>
      </div>
      {/* review */}
      <div className=' rounded-lg flex bg-gray-100 border-1 border-gray-200 p-4 flex-col gap-4'>
        <div className='flex justify-between pt-2 v t-2'>
          <p className='!text-bodyText/70'>Package</p>
          <p className='!text-sm text-black'>{offerType} · {isFragile ? 'Fragile' : 'Not Fragile'}</p>
        </div>
        <div className='flex border-t border-bodyText/30 gap-4 border-dotted justify-between pt-4  '>
          <p className='!text-bodyText/70'>Image</p>
          <p className='!text-sm text-right'>{offerImage ? offerImage.name : 'No image uploaded'}</p>
        </div>
        <div className='flex border-t border-bodyText/30 gap-4 border-dotted justify-between pt-4  '>
          <p className='!text-bodyText/70'>Pickup & Destination</p>
          <p className='!text-sm text-right'>{from} to {to}</p>
        </div>
        <div className='flex border-t border-bodyText/30 gap-4 border-dotted justify-between pt-4  '>
          <p className='!text-bodyText/70'>Your Offer</p>
          <p className='!text-sm text-right'>₦{Number(amount).toLocaleString()}</p>
        </div>
        <div className='flex border-t border-bodyText/30 gap-4 border-dotted justify-between pt-4  '>
          <p className='!text-bodyText/70'>Urgent</p>
          <p className='!text-sm text-right'>{isUrgent ? 'Yes (+500 bonus)' : 'No'}</p>
        </div>
        <div className='flex border-t border-bodyText/30 gap-4 border-dotted justify-between pt-4  '>
          <p className='!text-bodyText/70'>Receiver's Name</p>
          <p className='!text-sm text-right'>{receiverName}</p>
        </div>
        <div className='flex border-t border-bodyText/30 gap-4 border-dotted justify-between pt-4  '>
          <p className='!text-bodyText/70'>Receiver's Contact</p>
          <p className='!text-sm text-right'>{receiverContact}</p>
        </div>
      </div>
      {/* Continue Button */}
      <Button
        title="Post Offer"
        onClick={handlePostOffer}
      />
    </div>
  );
};