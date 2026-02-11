import { Link, useLocation } from "react-router-dom";
import { useEffect } from "react";

import { useAppSelector, useAppDispatch } from "../../hooks";
import { useGetOrderItemNumberQuery, useGetUserProfileQuery } from "../../utils/ApiService";
import { logout, setCredentials } from "../../features/auth/authSlice";

const Header: React.FC = () => {
  const location = useLocation();
  const user = useAppSelector((state) => state.auth.userInfo);
  const dispatch = useAppDispatch();
  // const { data } = useGetUserProfileQuery("userDetails", {
  //   // perform a refetch every 15mins * 60 second * 1000 milisecond
  //   pollingInterval: 900000,
  // });

  // useEffect(() => {
  //   if (data) dispatch(setCredentials(data));
  // }, [data, dispatch]);

  const { data: orderItemNumber } = useGetOrderItemNumberQuery();

  const handleLogout = () => {
    dispatch(logout());
  };

  const tenantName: string = "İDAY";
  const middle: number = Math.ceil(tenantName.length / 2);

  return (
    <div className="site-navbar py-2">
      <div className="container">
        <div className="d-flex align-items-center justify-content-between">
          <div className="logo">
            <div className="site-logo">
              <Link to="/" className="js-logo-clone">
                <strong className="text-primary">
                  {tenantName.slice(0, middle)}
                </strong>
                {tenantName.slice(middle)}
              </Link>
            </div>
          </div>
          {user ? (
            <>
              <div className="main-nav d-none d-lg-block">
                <nav
                  className="site-navigation text-right text-md-center"
                  role="navigation"
                >
                  <ul className="site-menu js-clone-nav d-none d-lg-block">
                    <li className={location.pathname === "/" ? "active" : ""}>
                      <Link to="/">Ana Sayfa</Link>
                    </li>
                    <li
                      className={location.pathname === "/store" ? "active" : ""}
                    >
                      <Link to="/store">İlaçlar</Link>
                    </li>
                    <li>
                      <Link to="/contact">İletişim</Link>
                    </li>
                  </ul>
                </nav>
              </div>
              <div className="icons">
                <a href="#" className="icons-btn d-inline-block js-search-open">
                  <span className="icon-search"></span>
                </a>
                <Link to="/cart" className="icons-btn d-inline-block bag">
                  <span className="icon-shopping-bag"></span>
                  <span className="number">{orderItemNumber}</span>
                </Link>

                {/* //This iplementation is not correct!!!
                // Look at Console */}
                <Link to="/profile" className="icons-btn d-inline-block user">
                  <div className="main-nav d-inline-block">
                    <nav className="site-navigation text-right text-md-center" role="navigation">
                      <ul className="site-menu js-clone-nav d-inline-block">
                        <li className="has-children">
                          <span className="icon-user "></span>
                          <ul className="dropdown">
                            <li><a href="#">Hesabım</a></li>
                            <li><a href="#">Siparişlerim</a></li>
                            <li>
                              <a href="#" className="logout-link" onClick={handleLogout}>Çıkış Yap</a>
                            </li>
                          </ul>
                        </li>
                      </ul>
                    </nav>
                  </div>
                </Link>
                
              </div>
              <div className="search-wrap">
                <div className="container">
                  <a href="#" className="search-close js-search-close">
                    <span className="icon-close2"></span>
                  </a>
                  <form action="#" method="post">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Search keyword and hit enter..."
                    />
                  </form>
                </div>
              </div>
            </>
          ) : (
            <div className="main-nav d-none d-lg-block">
              <nav
                className="site-navigation text-right text-md-center"
                role="navigation"
              >
                <ul className="site-menu js-clone-nav d-none d-lg-block">
                  <li>
                    <Link to="/login">Giriş Yap</Link>
                  </li>
                </ul>
              </nav>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Header;
