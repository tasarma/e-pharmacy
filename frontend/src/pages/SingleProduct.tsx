import {useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  useGetSingleProductQuery,
  useGetProductSpesificationsQuery,
  useGetProductOrderInfoQuery,
  useGetOrderItemNumberQuery,
} from "../utils/ApiService";
import { useAppDispatch } from "../hooks";
import { createOrderItems } from "../features/order/orderSlice";

function SingleProduct() {
  const [qty, setQuantity] = useState<number>(0);
  const dispatch = useAppDispatch();

  const handleQuantityChange = (amount: number) => {
    setQuantity((prev) => Math.max(0, prev + amount));
  };

  const { productId } = useParams<{ productId: string }>();
  const {data: product } = useGetSingleProductQuery(productId || '1');
  const {data: productSpesifications } = useGetProductSpesificationsQuery(productId || '1');
  const {data: productOrderingInformations } = useGetProductOrderInfoQuery(productId || '1');
  const { data: orderItemNumber, refetch } = useGetOrderItemNumberQuery();

   const saveOrderItem = async () => {
    const orderItem = {
      productId,
      qty,
    };

    await dispatch(createOrderItems(orderItem));
    refetch();
  };


  if (!product || !productSpesifications || !productOrderingInformations) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <div className="bg-light py-3">
        <div className="container">
          <div className="row">
            <div className="col-md-12 mb-0">
              <Link to="/">Ana Sayfa</Link> <span className="mx-2 mb-0">/</span>
              <Link to="/store">İlaçlar</Link>{" "}
              <span className="mx-2 mb-0">/</span>
              <strong className="text-black">{product.name}</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="site-section">
        <div className="container">
          <div className="row">
            <div className="col-md-5 mr-auto">
              <div className="border text-center">
                <img
                  src={product.image}
                  alt="Image"
                  className="img-fluid p-5"
                />
              </div>
            </div>
            <div className="col-md-6">
              <h2 className="text-black">{product.name}</h2>
              <p>{product.contents}</p>
              <p className="text-primary h4">
                {product.sale_price ? (
                  <>
                    ₺ <del>{product.price}</del> &mdash; ₺{product.sale_price}
                  </>
                ) : (
                  <>₺{product.price}</>
                )}
              </p>

              <div className="mb-5">
                <div className="input-group mb-3" style={{ maxWidth: "220px" }}>
                  <div className="input-group-prepend">
                    <button
                      className="btn btn-outline-primary"
                      type="button"
                      onClick={() => handleQuantityChange(-1)}
                    >
                      -
                    </button>
                  </div>
                  <input
                    type="text"
                    className="form-control text-center"
                    value={qty}
                    readOnly
                  />
                  <div className="input-group-append">
                    <button
                      className="btn btn-outline-primary"
                      type="button"
                      onClick={() => handleQuantityChange(1)}
                    >
                      +
                    </button>
                  </div>
                </div>
              </div>
              <p>
                <button
                  className="buy-now btn btn-sm height-auto px-4 py-3 btn-primary"
                  onClick={() => saveOrderItem()}
                >
                  Sepete Ekle
                </button>
              </p>

              <div className="mt-5">
                <ul
                  className="nav nav-pills mb-3 custom-pill"
                  id="pills-tab"
                  role="tablist"
                >
                  <li className="nav-item">
                    <a
                      className="nav-link active"
                      id="pills-home-tab"
                      data-toggle="pill"
                      href="#pills-home"
                      role="tab"
                      aria-controls="pills-home"
                      aria-selected="true"
                    >
                      Ürün Bilgileri
                    </a>
                  </li>
                  <li className="nav-item">
                    <a
                      className="nav-link"
                      id="pills-profile-tab"
                      data-toggle="pill"
                      href="#pills-profile"
                      role="tab"
                      aria-controls="pills-profile"
                      aria-selected="false"
                    >
                      Ürün Detayları
                    </a>
                  </li>
                </ul>
                <div className="tab-content" id="pills-tabContent">
                  <div
                    className="tab-pane fade show active"
                    id="pills-home"
                    role="tabpanel"
                    aria-labelledby="pills-home-tab"
                  >
                    <table className="table custom-table">
                      <thead>
                        <tr>
                          <th>Malzeme</th>
                          <th>Açıklama</th>
                          <th>Paketleme</th>
                        </tr>
                      </thead>
                      <tbody>
                        {productOrderingInformations.map((info, index) => (
                          <tr key={index}>
                            <td>{info.material}</td>
                            <td>{info.description}</td>
                            <td>{info.packaging}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div
                    className="tab-pane fade"
                    id="pills-profile"
                    role="tabpanel"
                    aria-labelledby="pills-profile-tab"
                  >
                    <table className="table custom-table">
                      <tbody>
                        {productSpesifications.map((spec, index) => (
                          <tr key={index}>
                            <td>{spec.key}</td>
                            <td className="bg-light">{spec.value}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SingleProduct;
