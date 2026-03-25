import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../SignInLayout/style.css'
import { PhoneInput } from './PhoneInput';
import PhoneVerification from './PhoneVerification';
import { IdentityVerification } from './IdentityVerification';
import { FaceVerification } from './FaceVerification';
import { Congratulations } from './congratulations';
import api from '../../api/axios';

const VerifyLayout = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<number>(1);
  const [phone, setPhone] = useState<string>("");
  const [identificationData, setIdentificationData] = useState<any>(null);
  const [faceData, setFaceData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  /**
   * Helper: Converts Base64 string from webcam to a File object
   * matches what Django's ImageField expects.
   */
  const dataURLtoFile = (dataurl: string, filename: string) => {
    const arr = dataurl.split(',');
    const mime = arr[0].match(/:(.*?);/)![1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
  };

  useEffect(() => {
    const triggerVerificationFlow = async () => {
      // Logic only triggers once faceData is captured and loading is true
      if (!isLoading || !faceData) return;

      try {
        const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
        const userId = storedUser.id;

        if (!userId) {
          console.error("User session missing");
          setIsLoading(false);
          return;
        }

        /**
         * 1. Update Profile (Phone & Avatar)
         */
        const profileFormData = new FormData();
        profileFormData.append('phone_number', phone);
        profileFormData.append('type', 'carrier');
        profileFormData.append('is_new_user', "false"); 
        
        const base64Image = faceData.image || faceData; 
        if (base64Image && typeof base64Image === 'string') {
          const imageFile = dataURLtoFile(base64Image, `avatar_${userId}.jpg`);
          // Use 'image' as key to match ProfileSerializer
          profileFormData.append('image', imageFile);
        }

        console.log("Submitting Profile Update...");
        const profileResponse = await api.patch(`/users/${userId}/profiles/`, profileFormData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });

        /**
         * 2. Create Verification Record (ID details)
         */
        if (identificationData) {
          console.log("Submitting Verification Record...");
          // This should be a POST to your verification endpoint
          await api.patch(`/users/${userId}/profiles/`, {
            verification_type: identificationData.type,
            id_number: identificationData.number,
          });
        }

        /**
         * 3. Sync Local Storage
         * Update the stored user object so other parts of the app see the changes
         */
        const updatedUser = {
            ...storedUser,
            profile: profileResponse.data 
        };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        console.log("✅ Local storage synced and backend updated.");

        // Move to final step
        setStep(5);

      } catch (error: any) {
        const errorData = error.response?.data;
        console.error("❌ API Error:", errorData || error.message);
        
        // Handle nested error objects from DRF
        const errorMessage = typeof errorData === 'object' 
          ? Object.values(errorData).flat()[0] 
          : "Could not complete verification. Please check your details.";
          
        alert(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    triggerVerificationFlow();
  }, [isLoading, faceData]);

  return (
    <div className="background !justify-start">
      <div className="gradient-layer-alt" />
      
      <div className={`px-8 w-full flex items-center ${step > 1 ? 'justify-between' : 'justify-end'} my-12`}>
        {step > 1 && step < 5 && (
          <button 
            onClick={() => setStep(prev => prev - 1)} 
            className="p-2 -ml-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        )}
        
        {step < 5 && (
          <div className="flex gap-1">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className={`h-1 w-8 rounded-full ${i <= step ? 'bg-blue-700' : 'bg-blue-100'}`} />
            ))}
          </div>
        )}
      </div>
      
      <div className='w-full'>
        {step === 1 && <PhoneInput setStep={setStep} setPhone={setPhone} />}
        {step === 2 && <PhoneVerification phone={phone} setStep={setStep}/>}
        {step === 3 && <IdentityVerification setIdentificationData={setIdentificationData} setStep={setStep} />}
        {step === 4 && (
          <FaceVerification 
            loading={isLoading} 
            setFaceData={setFaceData} 
            setIsLoading={setIsLoading} 
            setStep={setStep}
          />
        )}
        {step === 5 && <Congratulations />}
      </div>
    </div>
  );
};

export default VerifyLayout;