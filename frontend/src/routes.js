import React from "react";

// Admin Imports
import MainDashboard from "views/admin/default";
import NFTMarketplace from "views/admin/marketplace";
import AdStudio from "views/admin/profile";
import DataTables from "views/admin/tables";
import TestingDashboard from "views/admin/testing";
import RTLDefault from "views/rtl/default";
import CompanyProfile from "views/admin-company/profile";
import Products from "views/admin-company/products";
import NewProduct from "views/admin-company/newProducts";
// Auth Imports
import SignIn from "views/auth/SignIn";

// Icon Imports
import {
  MdHome,
  MdOutlineShoppingCart,
  MdBarChart,
  MdSpaceDashboard,
  MdLock,
  MdAdd,
} from "react-icons/md";

const routes = [
    {
    name: "Ad Studio",
    layout: "/admin",
    path: "creator",
    icon: <MdSpaceDashboard className="h-6 w-6" />,
    component: <AdStudio />,
  },
  {
    name: "Products",
    layout: "/admin",
    path: "default",
    icon: <MdHome className="h-6 w-6" />,
    component: <MainDashboard />,
  },
  {
    name: "Sign In",
    layout: "/auth",
    path: "sign-in",
    icon: <MdLock className="h-6 w-6" />,
    component: <SignIn />,
  },
  {
    name: "Company Profile",
    layout: "/admin-company",
    path: "profile",
    icon: <MdSpaceDashboard className="h-6 w-6" />,
    component: <CompanyProfile />,
  },
  {
    name: "New Product",
    layout: "/admin-company",
    path: "new-product",
    icon: <MdAdd className="h-6 w-6" />,
    component: <NewProduct />,
  },
  {
    name: "Products",
    layout: "/admin-company",
    path: "products",
    icon: <MdHome className="h-6 w-6" />,
    component: <Products />,
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
