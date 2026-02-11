import { Outlet } from "react-router-dom";

import Footer from "./Footer";
import Header from "./Header";

function Layout({ product }: any) {
  return (
    <>
      <div className="site-wrap">
        <Header />
        <main>
          <Outlet />
        </main>
        <Footer />
      </div>
    </>
  );
}

export default Layout;
