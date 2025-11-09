import React from "react";

// Admin Imports
import MainDashboard from "views/admin/default";
import NFTMarketplace from "views/admin/marketplace";
import ContentCreator from "views/admin/profile";
import DataTables from "views/admin/tables";
import TestingDashboard from "views/admin/testing";
import RTLDefault from "views/rtl/default";

// Auth Imports
import SignIn from "views/auth/SignIn";

// Icon Imports
import {
  MdHome,
  MdOutlineShoppingCart,
  MdBarChart,
  MdSpaceDashboard,
  MdLock,
} from "react-icons/md";

const routes = [
    {
    name: "Content Creator",
    layout: "/admin",
    path: "creator",
    icon: <MdSpaceDashboard className="h-6 w-6" />,
    component: <ContentCreator />,
  },
  {
    name: "Products",
    layout: "/admin",
    path: "default",
    icon: <MdHome className="h-6 w-6" />,
    component: <MainDashboard />,
  },
  {
    name: "NFT Marketplace",
    layout: "/admin",
    path: "nft-marketplace",
    icon: <MdOutlineShoppingCart className="h-6 w-6" />,
    component: <NFTMarketplace />,
    secondary: true,
  },
  {
    name: "Data Tables",
    layout: "/admin",
    icon: <MdBarChart className="h-6 w-6" />,
    path: "data-tables",
    component: <DataTables />,
  },

  {
    name: "API Testing",
    layout: "/admin",
    path: "testing",
    icon: <MdBarChart className="h-6 w-6" />,
    component: <TestingDashboard />,
  },
  {
    name: "Sign In",
    layout: "/auth",
    path: "sign-in",
    icon: <MdLock className="h-6 w-6" />,
    component: <SignIn />,
  },
  // {
  //   name: "RTL Admin",
  //   layout: "/rtl",
  //   path: "rtl",
  //   icon: <MdHome className="h-6 w-6" />,
  //   component: <RTLDefault />,
  // },
];
export default routes;
