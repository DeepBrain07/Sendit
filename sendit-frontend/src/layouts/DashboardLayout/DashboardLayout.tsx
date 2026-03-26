import { Icon } from "@iconify/react";
// import { logo, } from "../../assets/images";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

function DashboardLayout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const currentPath = window.location.pathname;
  const menu = {
    "Home": ["iconamoon:profile", "/home"],
    "Offers": ["mdi:package-outline", "/offers"],
    "Chat": ["humbleicons:chat", "/chats"],
    "Wallet": ["streamline-plump:wallet", "/wallet"],
    "Profile": ["iconamoon:profile", "/profile"],
  }
  return (
    <div className="w-full overflow-hidden">
      <div className="mb-[100px]">
        {children}
      </div>
      <div className="bg-white shadow-2xl z-50 flex justify-between overflow-x-scroll fixed bottom-0 w-full">
        {Object.entries(menu).map(([name, [icon, path]]) => (
          <div key={name} onClick={() => navigate(path)} className={`cursor-pointer flex-1 p-4 flex ${path === currentPath ? "text-primary" : "text-black/80" }  flex-col items-center justify-center`}>
            <Icon icon={icon} width={24} className=""/>
            <p className="!font-bold mt-1">{name}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default DashboardLayout;
