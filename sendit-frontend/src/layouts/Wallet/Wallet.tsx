import DashboardLayout from "../DashboardLayout/DashboardLayout"
import GradientBackground from "../../components/GradientBackground"
import { useNavigate } from "react-router-dom";
import { Icon } from "@iconify/react/dist/iconify.js";
import { useState } from "react";
import AddMoneyModal from "./AddMoneyModal"; // Adjust path as necessary
import WithdrawMoneyModal from "./WithdrawMoneyModal";
import BankDetailsModal from "./BankDetailsModal";

const Wallet = () => {
    const navigate = useNavigate();
    const [isAddMoneyModalOpen, setIsAddMoneyModalOpen] = useState(false);
    const [isWithdrawMoneyModalOpen, setIsWithdrawMoneyModalOpen] = useState(false);
    const [isBankDetailsModalOpen, setIsBankDetailsModalOpen] = useState(false);


    return (
        <DashboardLayout>
            {/* The Integrated Modal */}
            <AddMoneyModal 
                isAddMoneyModalOpen={isAddMoneyModalOpen} 
                setIsAddMoneyModalOpen={setIsAddMoneyModalOpen} 
            />
            <WithdrawMoneyModal 
                isWithdrawMoneyModalOpen={isWithdrawMoneyModalOpen} 
                setIsWithdrawMoneyModalOpen={setIsWithdrawMoneyModalOpen} 
            />
            <BankDetailsModal 
                isModalOpen={isBankDetailsModalOpen} 
                setIsModalOpen={setIsBankDetailsModalOpen} 
            />

            <div className="background !justify-start !flex !flex-col">
                <div className="gradient-layer-alt2 flex flex-col p-4 pr-8 pt-8 gap-12 !text-white !h-fit">
                    <div className='flex items-center justify-start gap-4'>
                        <button onClick={() => navigate('/home')} className="p-2 bg-white rounded-[50%] hover:bg-gray-100 transition-colors">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                        </button>
                        <h2 className="!text-xl">Wallet</h2>
                    </div>
                    <GradientBackground >
                        <div className="flex flex-col items-start ">
                            <p className="text-gray-300 !text-sm">Available Balance</p>
                            <h1 className="!font-bold !text-2xl">₦12,500</h1>
                        </div>
                        <div className="w-full mt-4 rounded-xl flex items-center text-center justify-between gap-2 !text-black/80">
                            
                            <div onClick={() => setIsAddMoneyModalOpen(true)} className="hover:bg-gray-100 flex flex-col w-fit items-center bg-white p-2 px-4 gap-1 cursor-pointer rounded-xl">
                                <Icon icon="carbon:add-filled" width={24} className="shrink-0 text-primary"/>
                                <p className="!text-xs !font-black !text-black">Add Money</p>
                            </div>
                            <div onClick={() => setIsWithdrawMoneyModalOpen(true)} className="hover:bg-gray-100 flex flex-col w-fit items-center bg-white p-2 px-4 gap-1 cursor-pointer rounded-xl">
                                <Icon icon="uil:money-withdrawal" width={24} className="shrink-0 text-primary"/>
                                <p className="!text-xs !font-black !text-black">Withdraw Money</p>
                            </div>
                            <div onClick={() => setIsBankDetailsModalOpen(true)} className="hover:bg-gray-100 flex flex-col w-fit items-center bg-white p-2 px-4 gap-1 cursor-pointer rounded-xl">
                                <Icon icon="boxicons:bank-filled" width={24} className="shrink-0 text-primary"/>
                                <p className="!text-xs !font-black !text-black">Bank Details</p>
                            </div>
                        </div>
                    </GradientBackground>
                </div>
                {/* Recent Transactions */}
                <div className="mt-[320px] flex flex-col pr-8 items-start w-full p-4">
                    <div className="flex items-center w-full justify-between gap-4">
                        <p className="!font-black !text-black">Recent Transactions</p>
                        <p className="!font-black cursor-pointer hover:underline !text-primary !text-xs">See all</p>
                    </div>
                    <div className="flex flex-col w-full gap-4 mt-4">
                        <TransactionCard 
                            type="deposit" 
                            amount={10000} 
                            status="Successful" 
                            date="2023-10-15" 
                            description="Received money from John Doe" 
                        />
                        <TransactionCard 
                            type="withdrawal" 
                            amount={5000} 
                            status="Failed" 
                            date="2023-10-14" 
                            description="Withdrew money for groceries" 
                        />
                        <TransactionCard 
                            type="delivery" 
                            amount={2500}
                            status="Pending"
                            date="2023-10-13" 
                            description="Payment for package delivery to Lagos" 
                        />
                    </div>
                </div>
            </div>
        </DashboardLayout>
    )
}

const TransactionCard = ({type, amount, status, date, description}: {type: 'deposit' | 'withdrawal' | 'delivery', amount: number, status: 'Successful' | 'Failed' | 'Pending', date: string, description: string}) => {
    return (
        <div className="flex items-start justify-between gap-4 w-full p-4 px-2 bg-gray-100 border-1 border-gray-200 rounded-xl">
            <div className="flex items-start gap-2">
                <div className="p-2 bg-white rounded-[50%]">
                    <Icon icon={type === 'deposit' ? "carbon:add-filled" : type === 'withdrawal' ? "clarity:bank-solid" : "mage:package-box-fill"} width={24} className="shrink-0 text-primary"/>
                </div>
                <div className="flex flex-col gap-1">
                    <p className="!font-black !text-sm !text-black">{description}</p>
                    <div className={`flex items-center gap-1 p-1 px-2 rounded-full w-fit !text-xs ${status === 'Successful' ? 'bg-green-100 text-green-500' : status === 'Failed' ? 'bg-red-100 text-red-500' : 'bg-yellow-100 text-yellow-500'}`}>
                        <Icon icon={status === 'Successful' ? "lets-icons:check-fill" : status === 'Failed' ? "material-symbols:error-outline" : "ph:warning-circle-bold"} width={16} className={`${status === 'Successful' ? 'text-green-500' : status === 'Failed' ? 'text-red-500' : 'text-yellow-500'}`}/>
                        <p className={`mt-[1.5px] !text-xs ${status === 'Successful' ? '!text-green-500' : status === 'Failed' ? '!text-red-500' : '!text-yellow-500'}`}>
                            {status}
                        </p>
                    </div>
                    <p className="!text-xs !text-gray-500">{date}</p>
                </div>
            </div>
            <div className="flex flex-col items-end">
                <p className={`!font-bold ${type === 'deposit' ? '!text-green-500' : type === 'withdrawal' ? '!text-red-500' : '!text-blue-500'}`}>
                    {type === 'deposit' ? '+ ' : type === 'withdrawal' ? '- ' : ''}₦{amount.toLocaleString()}
                </p>
            </div>
        </div>
    )
}

export default Wallet;