import { Icon } from '@iconify/react/dist/iconify.js';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/Button';
import { useState } from 'react';
import { bgGradient } from '../../assets/images';

const USER_AVATAR_URL = "https://randomuser.me/api/portraits/men/32.jpg";

interface Message {
  id: number;
  type: 'sent' | 'received';
  text: string;
  time: string;
}

const SpecificChat = () => {
    const navigate = useNavigate();
    const chatId = window.location.pathname.split('/').pop(); 
    const [messages, setMessages] = useState<Message[]>([
    { id: 1, type: 'sent', text: "Hello, where can we meetup? So that you can pick-up the package.", time: "8:43 PM" },
    { id: 2, type: 'received', text: "We can meet at the garage at berger ma. Is that okay ma?", time: "8:45 PM" },
  ]);
  const [newMessage, setNewMessage] = useState("");
  const title = "Package to Lagos";
    const boxSize = "Small Box";
    const status = "Fragile";

  const handleSend = () => {
    if (newMessage.trim()) {
      // Add logic to send message
      console.log("Sending message:", newMessage);
      setNewMessage("");
    }
  };
    return (
        <div className=''>
            {/* Chat header */}
            <div className="z-50 fixed shadow-sm bg-white w-full top-0 p-4 flex gap-4 justify-between items-center">
                <div className={` w-full flex items-center gap-4 py-2  `}>
                    <button onClick={() => navigate('/chats')} className=" border-1  border-gray-100 p-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                    </button>
                    {/* User details */}
                    <div className='flex gap-1'>
                        <img src="https://randomuser.me/api/portraits/men/32.jpg" alt="User profile" className='border-1 border-primary w-10 h-10 rounded-full object-cover' />
                        <div>
                            <div className='flex items-center'>
                                <h2 className='!text-sm'>John Doe</h2>
                                <Icon icon="fluent-mdl2:verified-brand-solid" width={16} className="text-primary inline-block ml-1" />
                            </div>
                            <div className='flex text-green-500 items-center '>
                                <Icon icon="stash:circle-dot-duotone" width={16} className="shrink-0" />
                                
                                {/* <Icon icon="material-symbols-light:circle" width={2} className="shrink-0" />   */}
                                <p className='!text-xs mt-1'>Surulere → Ibadan</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div className='flex items-center  gap-2'>
                    <Icon icon="solar:phone-outline" width={28} className="cursor-pointer pt-1 text-bodyText/80" />
                    <Icon icon="iwwa:option" height={30} className="text-bodyText/80 cursor-pointer" />
                </div>
            </div>
            {/* Chat messages */}
            <div className='mt-[90px] bg-gray-100 flex-1 flex flex-col gap-4'>
                <div className='flex w-full bg-blue-100 p-2 justify-center'>
                    <p className='font-black !text-xs'>Messages are end-to-end encrypted</p>
                </div>
                <div className='p-4 flex flex-col gap-4 items-center'>
                    <p className='font-black !text-[11px]'>🎉 You accepted this offer</p>
                    <div className='w-full rounded-xl bg-white border-1 border-gray-100'>
                        {/* background */}
                        <div className="">
                            <div className="package-card h-fit ">
                                
                                {/* 1. Background Image */}
                                <img src={bgGradient} alt="Package" className=" background-image rounded-t-xl" />

                                {/* 2. Text Content Overlay */}
                                <div className="card-overlay  ">
                                    <p className="package-title !text-xl !font-bold">{title}</p>
                                    
                                    {/* 3. Row of Tags */}
                                    <div className="tag-row">
                                        <div className="tag">
                                            {/* Box Emoji */}
                                            <span className='!text-sm' role="img" >📦 {boxSize}</span>
                                            
                                        </div>
                                        
                                        <div className="tag">
                                            <span  className='!text-sm'>{status}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                        </div>
                        {/* Content */}
                        <div className='w-full'>
                            <div className='p-2 w-full'>
                                <div className='w-full flex justify-between pt-2   border-bodyText/30 '>
                                    <p className='!text-sm !text-bodyText/70'>From</p>
                                    <p className='!text-sm text-bodyText/70'>To</p>
                                </div>
                                
                                <div className='w-full flex justify-between py-2 items-center  border-bodyText/30 '>
                                    <p className='!text-sm !text-bodyText'>Osun</p>
                                    <Icon icon="solar:arrow-right-linear" width={20} className="text-bodyText/70 shrink-0" />
                                    <p className='!text-sm text-bodyText'>Lagos</p>
                                </div>
                                <div className='w-full flex justify-between pt-2    border-bodyText/30 '>
                                    <p className='!text-xs !text-bodyText/70'>Escrow ( Sender Paid)</p>
                                    <p className='!text-xs text-bodyText/70'>₦3,500</p>
                                </div>
                                
                                <div className='w-full flex justify-between pt-2   border-bodyText/30 '>
                                    <p className='!text-xs !text-bodyText/70'>Platform fee (10%)</p>
                                    <p className='!text-xs text-red-500'>-₦350</p>
                                </div>
                                <div className='w-full flex justify-between pt-2    border-bodyText/30 '>
                                    <p className='pt-2 !text-sm !text-bodyText'>You Pay</p>
                                    <p className='pt-2 !text-sm !text-bodyText'>₦3,850</p>
                                </div>
                            </div>
                            <div className='rounded-b-xl flex flex-col gap-4 justify-center items-center w-full bg-blue-100 p-4'>
                                <Button onClick={() => {navigate('/sender/1')}} title='View Sender Dashboard'/>
                                <p className='!text-sm !text-black'>See payment status & delivery timeline</p>
                            </div>
                        </div>
                    </div>
                </div>
                {/* messaging */}
                <div className="w-full h-screen flex flex-col  relative overflow-hidden">

                    {/* 2. Scrollable Message Area */}
                    <main className="flex-1 w-full px-6 py-6 overflow-y-auto space-y-6 pb-28">
                        {messages.map((message) => (
                        <div key={message.id} className={`flex items-start gap-3 w-full ${message.type === 'sent' ? 'justify-end' : 'justify-start'}`}>
                            
                            {/* Show avatar only for received messages */}
                            {message.type === 'received' && (
                            <img src={USER_AVATAR_URL} alt="User Avatar" className="w-10 h-10 rounded-full shrink-0 mt-1" />
                            )}
                            
                            <div className={`flex flex-col gap-1.5 max-w-[80%] ${message.type === 'sent' ? 'items-end' : 'items-start'}`}>
                            <div className={`p-4 ${message.type === 'sent' 
                                ? 'bg-blue-600 text-white rounded-[20px] rounded-tr-[0px]' 
                                : 'bg-gray-200 text-black rounded-[20px] rounded-tl-[0px]'}`}>
                                <p className="!text-sm leading-relaxed">{message.text}</p>
                            </div>
                            <span className="!text-xs text-gray-400 font-medium">{message.time}</span>
                            </div>
                        </div>
                        ))}
                    </main>

                    {/* 3. Fixed Bottom Input Bar */}
                    <footer className="w-full bg-white px-6 pt-4 pb-4 flex items-center gap-4 fixed bottom-0 left-0 border-t border-gray-100 z-10 shrink-0">
                        <div className="flex-1 flex items-center gap-3 bg-gray-50 border border-gray-200 rounded-full px-5 py-3.5 focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/10">
                        {/* <Icon icon="solar:paperclip-linear" className="text-gray-500 cursor-pointer" width={20} /> */}
                        <input 
                            type="text" 
                            value={newMessage}
                            onChange={(e) => setNewMessage(e.target.value)}
                            placeholder="Type a message..." 
                            className="flex-1 bg-transparent text-sm text-black outline-none"
                            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        />
                        </div>
                        
                        <button 
                        onClick={handleSend}
                        className={`p-4 bg-primary rounded-full flex items-center justify-center shadow-sm transition-all ${newMessage.trim() ? 'bg-blue-600' : 'bg-gray-200'}`}
                        >
                        <Icon icon="mynaui:send-solid" className="text-black" width={28} />
                        </button>
                    </footer>
                    </div>
            </div>
        </div>
    );
}

export default SpecificChat;