import { useNavigate, useParams } from "react-router-dom";
import { Icon } from "@iconify/react/dist/iconify.js";
import DashboardLayout from "./DashboardLayout";
import EscrowLifecycle from "../../components/EscrowLifecycle";
import { type LifecycleStep } from "../../components/EscrowLifecycle";
import GradientBackground from "../../components/GradientBackground";

const SenderDashboard = () => {
    const navigate = useNavigate();
    const senderId = useParams().senderId; // Get senderId from URL params
    const lifecycleData: LifecycleStep[] = [
        {
          id: 1,
          title: "Carrier Accepted",
          description: "Awaiting sender to fund escrow",
          completed: true,
          banner: "Sender must fund escrow before you do pickup. They've been notified",
        },
        {
          id: 2,
          title: "Escrow Activated",
          description: "Funds held by Sendit x Interswitch",
          completed: false
        },
        {
          id: 3,
          title: "Picked Up Package",
          description: "In carrier's hands - money still held",
          completed: false,
          action: {
            label: "Package picked Up",
            onClick: () => console.log("Picked up!")
          }
        },
        {
          id: 4,
          title: "On your way",
          description: "Carrier heading to destination",
          completed: false,
          action: {
            label: "Yes",
            onClick: () => console.log("Yes!")
          }
        },
        {
          id: 5,
          title: "Delivered",
          description: "Receiver, has received the package",
          completed: false,
          action: {
            label: "Confirm",
            onClick: () => console.log("Confirm!")
          }
        },
        {
          id: 6,
          title: "Dispute Window (12-24 hr)",
          description: "Receiver, has received the package",
          completed: false,
        },
      ];
      const from="Lagos";
      const to="Abuja";
      const verified = true;
      const rating = 4.5;
      const name = "John Doe";
      const amount = 5000;
      const date = "Today";
      const properties = ["Fragile", "Perishable"];
      const size = "Medium";
      const img = "https://randomuser.me/api/portraits/men/32.jpg";
    return (
        <div className='bg-[#FBFBFBB2] p-4 flex flex-col gap-8'>
            <div className={` w-full flex items-center gap-4  `}>
                <button onClick={() => navigate('/chats')} className="p-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </button>
                <h2 className="!text-xl">Sender Dashboard</h2>
            </div>
            <div className='flex flex-col gap-2'>
                    <p>Sender</p>
                    <div className='flex items-start gap-2 pt-2'>
                        <div className='border-1 border-primary size-12 rounded-lg bg-gray-300 shrink-0 flex items-center justify-center text-white'>
                            <img src={img} alt={name} className='w-full h-full object-cover rounded-lg shrink-0' />
                        </div>
                        <div className='flex flex-col'>
                            <p className='!text-sm !font-bold'>{name}</p>
                            <div className='flex items-center gap-1'>
                                {/* rating */}
                                <div className='flex jusify-center items-center gap-[1px] bg-gray-100 p-2 py-1 rounded-full'>
                                    <Icon icon="mdi:star" width={14} className="text-black"/>
                                    <p className='!text-xs  !mt-[1.5px] !text-black '>{rating}</p>
                                </div>
                                {verified && (
                                    <div className='flex jusify-center items-center gap-[1px] bg-gray-100 p-2 py-1 rounded-full'>
                                        <Icon icon="codicon:verified-filled" width={16} className="text-primary"/>
                                        <p className='!text-xs !font-extrabold !text-gray-500'>Verified</p>
                                    </div>
                                )}
                            </div>
                        </div>
                        {/* Buttons */}
                        <div className='mb-8 flex w-full gap-2 justify-end items-end text-black'>
                            <div className='p-2 rounded-[50%] bg-gray-100'>
                                <Icon icon="ant-design:message-filled" width={20} className="cursor-pointer"/>
                            </div>
                            <div className='p-2 rounded-[50%] bg-gray-100'>
                                <Icon icon="basil:phone-solid" width={20} className="cursor-pointer" />
                            </div>
                        </div>
                    </div>    
                    <GradientBackground>
                        <div className='flex flex-col gap-6 rounded-lg !text-white'>
                            <div className='flex justify-between items-center'>
                                <p >Awaiting Escrow</p>
                                <p className='!text-xs !font-bold rounded-full py-1 px-2 bg-primary/90 w-fit'>Pending</p>
                            </div>
                            <p className='!text-4xl !font-bold'>₦0</p>
                            <p className='!text-sm '>Sender has not funded escrow yet</p>
                        </div>
                    </GradientBackground>
                    {/* properties */}
                    <div className='mt-4 rounded-lg flex bg-gray-100 border-1 border-gray-200 p-4 flex-col gap-4'>
                        <p className='!font-black'>Package</p>
                        <div className='flex'>
                            <div className='p-2 rounded-lg bg-white flex justify-center items-center mr-2 h-fit shrink-0'>
                                <Icon icon="fluent:box-32-filled" width={24} className="text-primary inline-block shrink-0"/>
                            </div>
                            <div className='flex flex-col'>
                                <div className='flex items-center  flex-wrap'>
                                    <p className=' !font-bold inline-block '>{size} Box </p>
                                    {properties.map((property) => (
                                        <div key={property} className='flex  items-center '>
                                            <Icon icon="lucide:dot" width={24} className="inline-block text-black"/>
                                            <p  className="!font-bold">
                                                {property}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                                <p className=' !text-xs text-bodyText/80'>Ref #PK-01</p>
                            </div>
                        </div>
                        <div className=' flex justify-between pt-2 border-t-2 border-bodyText/30 border-dotted'>
                            <p className='!text-bodyText/70'>Pick-up</p>
                            <p className='!text-sm text-black'>📍 {from}</p>
                        </div>
                        <div className='flex justify-between pt-2  t-2  border-t-2 border-bodyText/30 border-dotted'>
                            <p className='!text-bodyText/70'>Destination</p>
                            <p className='!text-sm text-black'>📍 {to}</p>
                        </div>
                    </div>
                    {/* Lifecycle */}
                    <EscrowLifecycle steps={lifecycleData} />
                    {/* payout breakdown */}
                    <div className='mt-4 rounded-lg flex bg-gray-100 border-1 border-gray-200 p-4 flex-col gap-4'>
                        <p className='!font-black'>Payout Breakdown</p>
                        <div className='flex justify-between pt-2  t-2'>
                            <p className='!text-bodyText/70'>Escrow (Sender Paid)</p>
                            <p className='!text-sm text-black'>{amount}</p>
                        </div>
                        <div className='flex justify-between   '>
                            <p className='!text-bodyText/70'>Platform fee (10%)</p>
                            <p className='!text-sm text-red-500'>-₦350</p>
                        </div>
                        <div className='flex justify-between !text-xl pt-2  mt-[-4px]  border-t-2 border-bodyText/30 border-dotted'>
                            <p className='!text-black'>You Earn</p>
                            <p className=' !text-black'>₦3,150</p>
                        </div>
                    </div>
                    {/* Banner */}
                    <div className='mt-4 p-2 py-4 rounded-lg flex justify-center items-center bg-[#FFF9EB] border border-[#92400E] text-[#92400E] !text-4xl !font-bold'><p>Waiting for sender to fund escrow</p></div>
                </div>
        </div>

    );
};

export default SenderDashboard;