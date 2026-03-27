import  { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../SignInLayout/style.css'
import DashboardLayout from '../DashboardLayout/DashboardLayout';
import { Icon } from '@iconify/react/dist/iconify.js';
import { Button } from '../../components/Button';
import FundEscrowModal from '../Wallet/FundEscrowModal';
import api from '../../api/axios';
import toast, { Toaster } from 'react-hot-toast';

const Notifications = () => {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setLoading(true);
        const response = await api.get('/notifications/');
        const data = response.data.results?.results || [];
        setNotifications(data);
      } catch (error) {
        console.error("Error fetching notifications:", error);
        toast.error("Failed to load notifications");
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, []);

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <DashboardLayout>
      <Toaster position="top-center" reverseOrder={false} />
      
      <div className='bg-[#FBFBFBB2] p-4 flex flex-col gap-8'>
        <div className={` w-full flex items-center gap-4  `}>
          <button onClick={() => navigate('/home')} className="p-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <h2 className="!text-xl">Notifications</h2>
        </div>
      </div>

      <div className='p-2 flex flex-col w-full'>
        {loading ? (
          <div className="flex justify-center py-10">
            <Icon icon="line-md:loading-twotone-loop" width={40} className="text-primary" />
          </div>
        ) : notifications.length > 0 ? (
          notifications.map((notif) => (
            <NotificationCard 
              key={notif.id}
              proposalId={notif.id}
              title={notif.title}
              time={formatTime(notif.created_at)} 
              amount="2500" 
              carrierName="System Update" 
              to="Check details" 
              avatar="https://randomuser.me/api/portraits/lego/1.jpg" 
              isRead={notif.is_read}
            /> 
          ))
        ) : (
          <div className="text-center py-10 text-gray-500">No notifications yet</div>
        )}
      </div>
    </DashboardLayout>
  );
};

const NotificationCard = ({ proposalId, title, time, amount, carrierName, to, avatar, isRead }: { proposalId: number; title: string; time: string; amount: string; carrierName: string; to: string; avatar: string; isRead: boolean }) => {
    console.log("Notification is read:", isRead);
    console.log("Notification title:", to);
    const [isEscrowModalOpen, setIsEscrowModalOpen] = useState(false);
    const handleAction = async (action: 'accept' | 'reject') => {
        try {
            // Both actions directed to /accept/ per instructions
            await api.post(`/offers/proposals/${proposalId}/accept/`);
            toast.success(`Proposal ${action === 'accept' ? 'Accepted' : 'Rejected'}!`);
        } catch (error) {
            console.error(`Error during ${action}:`, error);
            toast.error(`Failed to ${action} proposal`);
        }
    }

    return (
        <div className={`flex flex-col border-b-2 border-gray-100 p-2 py-4 gap-2 `}>
            <FundEscrowModal 
                isModalOpen={isEscrowModalOpen} 
                setIsModalOpen={setIsEscrowModalOpen}
            />
            <div className='flex justify-between items-center'>
                <div className='flex items-center gap-2'>
                    <div className='p-2 rounded-[50%] bg-gray-100'>
                        <Icon icon="material-symbols:luggage-rounded" width={26} className="text-primary"/>
                    </div>
                    <p className='font-black !text-lg'>{title}</p>
                </div>
                <p className='!text-sm text-gray-400'>{time}</p>
            </div>
            
            <div className='flex flex-col gap-2'>
                <div className='flex gap-2 items-center'>
                    <h2 className="font-bold">₦{amount}</h2>
                    <div className='p-2 py-1 rounded-full w-fit flex justify-center items-center bg-primary'>
                        <Icon icon="codicon:thumbsup-filled" width={15} className="text-white"/>
                        <p className='!text-xs text-white ml-1 mt-1'>Bidding</p>
                    </div>
                </div>
                <div className='mt-3 flex gap-2'>
                    <div className='border-1 border-primary size-10 rounded-lg bg-gray-300 shrink-0 flex items-center justify-center text-white overflow-hidden'>
                        <img src={avatar} alt={carrierName} className='w-full h-full object-cover shrink-0' />
                    </div>
                    <div className='flex flex-col'>
                        <p className='!text-sm !font-bold'>{carrierName}</p>
                        <div className='flex items-center gap-1'>
                            <div className='flex justify-center items-center gap-[1px] bg-gray-100 px-2 py-0.5 rounded-full'>
                                <Icon icon="mdi:star" width={12} className="text-black" />
                                <p className='!text-[10px] !text-black '>4.2</p>
                            </div>
                            <Icon icon="codicon:verified-filled" width={14} className="text-primary" />
                        </div>
                    </div>
                </div>
            </div>

            <div className='flex justify-between gap-4 mt-2'>
                <Button 
                    title="Dismiss" 
                    onClick={() => handleAction('reject')} 
                    className='!bg-gray-100 !text-black !py-2 !text-xs'
                />
                <Button 
                    title="Accept Proposal" 
                    onClick={() => setIsEscrowModalOpen(true)} 
                    className='!py-2 !text-xs' 
                />
            </div>
        </div>
    );
}

export default Notifications;