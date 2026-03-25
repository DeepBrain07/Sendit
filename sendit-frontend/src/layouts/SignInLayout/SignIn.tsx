import { logo, bgLogo } from '../../assets/images';
import './style.css';
import { Button } from '../../components/Button';
import { useNavigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google'; // 1. Import hook
import axios from 'axios';

function SignIn() {
  const navigate = useNavigate();
  const BACKEND_URL = import.meta.env.VITE_API_BASE_URL;
  // 2. Define the login logic
  const login = useGoogleLogin({
  onSuccess: async (tokenResponse) => {
    try {
      console.log('Google Login Success, token response:', tokenResponse.access_token);
      const cleanToken = tokenResponse.access_token.trim();
      
      // 1. Send the token to the backend
      const response = await axios.post(
        `${BACKEND_URL}/users/google/login/`,
        { "id_token": cleanToken },
        { withCredentials: true } 
      );

      // 2. The backend returned: { status: 'Success', data: { user_info }, token: { ... } }
      console.log('Login Successful:', response.data);

      // 3. Save user data to your Global State (example using localStorage or a context)
      // We don't save the JWT token because it's already in the Cookie!
      localStorage.setItem('user', JSON.stringify(response.data.data));

      // 4. Navigate to the next step
      navigate('/onboarding');
      
    } catch (error:any) {
      console.error('Login Error details:', error.response?.data);
      alert('Authentication failed.');
    }
  },
});

  return (
    <div className="background">
      {/* Background Layers */}
      <div className="gradient-layer" />
      <div 
        className="image-layer" 
        style={{ backgroundImage: `url(${bgLogo})` }} 
      />

      {/* 1. Header Logo */}
      <div className="pt-16 w-full flex justify-center">
        <img src={logo} alt="Sendit" className="h-8" />
      </div>

      {/* 2. Middle Hero Text */}
      <div className=" px-8 text-center  my-24">
        <h1 className="text-white  font-extrabold leading-tight">
          Send it with <br /> someone going <br /> your way.
        </h1>
        <p className=" text-white mt-8 leading-relaxed">
          By continuing, you agree to the <span className="font-bold">Sendit Terms of Service</span>, and 
          acknowledge you've read our <span className="font-bold">Privacy Policy</span>
        </p>
      </div>

      {/* 3. Auth Buttons */}
      <div className="w-full flex flex-col items-center gap-4 px-6">
        {/* 3. Attach the login function to the onClick */}
        <Button 
          onClick={() => login()} 
          className='bg-white !text-black' 
          title='Continue with Google' 
          icon='devicon:google'
        />

        <Button onClick={() => navigate('/onboarding')} className='bg-white/50 !text-black' title='Continue with Apple' icon='devicon:apple'/>

        <p className="text-sm mt-4 text-bodyText/80">
          Already have an account? <span className="font-bold cursor-pointer text-bodyText" onClick={() => navigate('/onboarding')}>Log In</span>
        </p>
      </div>
    </div>
  );
}

export default SignIn;