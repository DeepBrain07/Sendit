import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../SignInLayout/style.css'
import DashboardLayout from '../DashboardLayout/DashboardLayout';
import { ProviderRoutePaths } from '../../routers/provider.router';
import { Icon } from '@iconify/react/dist/iconify.js';
import './style.css';

const Chats = () => {
  const navigate = useNavigate();
  return (
    <DashboardLayout >
        
        <div className='bg-[#FBFBFBB2] p-4 flex flex-col pb-8 gap-8'>
            <div className={` w-full flex items-center gap-4  `}>
                <button onClick={() => navigate('/home')} className="p-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </button>
                <h2 className="!text-xl">Chats</h2>
            </div>
        </div>

        {/* Chats */}
        <div className='py-4 flex flex-col '>
            <ChatCard
                name="John Doe"
                notifications={2}
                lastMessage="Hey, I just made the payment. Please check and confirm."
                profileImage="https://randomuser.me/api/portraits/men/32.jpg"
                lastMessageTime="2:45 PM"
                chatId="1"
            />
            <ChatCard
                name="John Doe"
                notifications={2}
                lastMessage="Hey, I just made the payment. Please check and confirm."
                profileImage="https://randomuser.me/api/portraits/men/32.jpg"
                lastMessageTime="2:45 PM"
                chatId="2"
            />
            <ChatCard
                name="John Doe"
                notifications={2}
                lastMessage="Hey, I just made the payment. Please check and confirm."
                profileImage="https://randomuser.me/api/portraits/men/32.jpg"
                lastMessageTime="2:45 PM"
                chatId="3"
            />

        </div>
      
    </DashboardLayout>
  );
};

const ChatCard = ({name, chatId, notifications, lastMessage, profileImage, lastMessageTime}: {name: string, chatId: string, notifications: number, lastMessage: string, profileImage: string, lastMessageTime: string}) => {
    const navigate = useNavigate();
    return (
        <div onClick={() => {navigate(ProviderRoutePaths.specificChat.replace(':chatId', chatId))}} className='cursor-pointer hover:bg-gray-100 flex items-center gap-4 bg-white p-4 rounded-xl'>
            <div className='relative'>
                <img src={profileImage} alt={`${name}'s profile`} className='border-1 border-primary w-12 h-12 rounded-full object-cover' />
                
            </div>
            <div className='flex-1'>
                <div className='flex justify-start items-center'>
                    <h3 className='font-bold'>{name}</h3>
                    <Icon icon="fluent-mdl2:verified-brand-solid" width={16} className="text-primary inline-block ml-1" />
                </div>
                
                <p className='!text-sm text-gray-500 w-[80%] overflow-hidden text-ellipsis'>{lastMessage}</p>
            </div>
            <div className='flex flex-col items-end gap-1'>
                
                <p className='!text-xs text-gray-500'>{lastMessageTime}</p>
                {notifications > 0 && (
                    <div className='bg-primary text-white !text-xs w-5 h-5 rounded-full flex items-center justify-center'>
                        <p className='!text-xs'>{notifications}</p>
                    </div>
                )}
            </div>
        </div>
    );

};

export default Chats;