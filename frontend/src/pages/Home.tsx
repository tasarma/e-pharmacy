import React from "react";

import backImage from "../images/hero_bg.jpg";

const Home: React.FC = () => {
  return (
    <div
      className="site-blocks-cover overlay"
      style={{ backgroundImage: `url(${backImage})` }}
    >
      <div className="container">
        <div className="row">
          <div className="col-lg-12 mx-auto align-self-center">
            <div className="site-block-cover-content text-center">
              <h1 className="mb-0">
                <strong className="text-primary">IDAY</strong> 7/24 Hizmetinizde
              </h1>
              <div className="row justify-content-center mb-5">
                <div className="col-lg-6 text-center">
                  <p>
                  Hızlı, güvenilir ve kaliteli ilaç hizmeti sunuyoruz. Modern tesislerimizle ürünlerinizi en iyi koşullarda saklıyor ve en kısa sürede ulaştırıyoruz.                  </p>
                </div>
              </div>
              <p>
                <a href="/store" className="btn btn-primary px-5 py-3">
                  Alışverişe Başla
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
