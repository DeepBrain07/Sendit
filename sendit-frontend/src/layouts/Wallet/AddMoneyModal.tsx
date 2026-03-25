import Modal from "../../components/Modal"
import { Button } from "../../components/Button"
import { useEffect, useState } from "react";
import { Icon } from "@iconify/react/dist/iconify.js"; // Added missing import

interface AddMoneyModalProps {
    isAddMoneyModalOpen: boolean;
    setIsAddMoneyModalOpen: (open: boolean) => void; // Added setter prop
}

const AddMoneyModal = ({ isAddMoneyModalOpen, setIsAddMoneyModalOpen }: AddMoneyModalProps) => {
    const [showCopyToast, setShowCopyToast] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);

    const [offer, setOffer] = useState<number>(2500);
    const presets = [2000, 4000, 6000, 8000, 10000];
    const accountNumber = "6239507606";

    // Countdown State (seconds)
    const [timeLeft, setTimeLeft] = useState(3030); // 50:30 in seconds

    const handleCopy = () => {
        navigator.clipboard.writeText(accountNumber).then(() => {
            setShowCopyToast(true);
            setTimeout(() => setShowCopyToast(false), 2000);
        });
    }

    // Reset success state when modal closes
    const handleCloseModal = () => {
        setIsAddMoneyModalOpen(false); // Now using the prop function
        setTimeout(() => setIsSuccess(false), 300);
    };

    useEffect(() => {
        if (!isAddMoneyModalOpen) return;

        const timer = setInterval(() => {
            setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
        }, 1000);

        return () => clearInterval(timer);
    }, [isAddMoneyModalOpen]);

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')} : ${secs.toString().padStart(2, '0')}`;
    };

    const updateOffer = (val: number) => {
        const newVal = Math.max(0, val);
        setOffer(newVal);
    };

    return (
        <Modal isOpen={isAddMoneyModalOpen} onClose={handleCloseModal} >
            {/* Copy Notification Toast */}
            {showCopyToast && (
                <div className="fixed top-10 left-1/2 -translate-x-1/2 z-[9999] bg-black/80 text-white px-4 py-2 rounded-full text-sm font-bold flex items-center gap-2 animate-in fade-in slide-in-from-top-4 duration-300">
                    <Icon icon="solar:check-circle-bold" className="text-green-400" />
                    Account number copied!
                </div>
            )}
            {!isSuccess ? (
                <div className="flex flex-col items-center  gap-4 ">
                    <h2 className="!font-black !text-lg"> Add Money to Wallet</h2>
                    <div className="flex flex-col  items-center gap-4 w-full mt-4">
                        <p className="!font-black">Enter Amount</p>
                        <div className="flex flex-col gap-2 w-full ">
                            <div className="flex flex-col items-center w-full gap-8 bg-white rounded-xl">
                                <div className="flex items-center gap-4">
                                    <div className="text-center">
                                        <div className="text-5xl font-black text-primary flex items-center justify-center">
                                            <span className="!text-[25px] !font-extrabold mr-1">₦</span>
                                            <h1>
                                                <input
                                                    type="number"
                                                    value={offer === 0 ? "" : offer}
                                                    onChange={(e) => updateOffer(Number(e.target.value))}
                                                    className="!text-4xl !font-black bg-transparent border-none outline-none max-w-[150px] text-center "
                                                    placeholder="0"
                                                />
                                            </h1>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex border-b-1 border-gray-200 pb-4 w-full  overflow-x-scroll justify-between  gap-2 !font-bold !text-bodyText/80">
                                    {presets.map((price) => (
                                        <button
                                            key={price}
                                            onClick={() => updateOffer(price)}
                                            className={`px-2 py-2 !text-xs rounded-xl font-bold transition-all ${offer === price ? "bg-primary text-white" : "bg-gray-50 hover:bg-gray-100"
                                                }`}
                                        >
                                            ₦{price.toLocaleString()}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center w-full flex-col gap-3 justify-between">
                            <p className="!font-black text-sm">Expires in</p>
                            <div className="px-3">
                                <p className="!font-bold text-black !text-2xl  tabular-nums">{formatTime(timeLeft)}</p>
                            </div>
                            <div className="w-full flex flex-col gap-1 rounded-lg p-4 px-2 border-1 border-[#CFD8FC] bg-[#F5F7FE]">
                                <div className="flex gap-4  justify-between">
                                    <p className="text-black !font-bold ">Moniepoint Ltd</p><p className="text-black !font-bold">{accountNumber}</p>
                                </div>
                                <div className="flex gap-4  text-bodyText/60  justify-between">
                                    <p className="!text-sm">Sendit/Mecry.p</p><p className="!text-sm !text-primary cursor-pointer hover:underline" onClick={handleCopy}>copy</p>
                                </div>
                            </div>
                            <div className="flex w-full gap-1 mb-4 justify-start items-center">
                                <Icon icon="carbon:information" width={20} className="shrink-0 " />
                                <p className="!text-sm mt-1">Transfer only ₦{offer.toLocaleString()} to the given account.</p>
                            </div>
                            <Button title="I have sent it" onClick={() => setIsSuccess(true)} />
                        </div>
                    </div>
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center py-12 px-4 text-center animate-in zoom-in duration-300">
                    <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-6">
                        <Icon icon="icon-park-solid:success" width={48} className="text-green-600" />
                    </div>
                    <h2 className="text-2xl font-black text-black mb-2">Transfer Received!</h2>
                    <p className="text-gray-500 mb-8">We are verifying your transaction. Your wallet will be updated shortly.</p>
                    <Button title="Back to Wallet" onClick={handleCloseModal} />
                </div>
            )}
        </Modal>
    )
}

export default AddMoneyModal;