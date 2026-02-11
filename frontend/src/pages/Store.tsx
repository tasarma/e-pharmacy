import Product from "../components/Product";
import { useAppDispatch, useAppSelector } from "../hooks";
import { fetchProducts } from "../features/product/productsSlice";
import { ProductType } from "../types";
import { useEffect } from "react";

import { useGetTenantProductsQuery } from "../utils/ApiService";

function Store() {

  // const products = useAppSelector((state) => state.products.items);
  const { data: products } = useGetTenantProductsQuery();
  const dispatch = useAppDispatch();

  // useEffect(() => {
  //   dispatch(fetchProducts());
  // }, [dispatch]);

  return (
    <div className="site-section bg-light">
      <div className="container">
        <div className="row">
          {products?.map((product: ProductType) => (
            <Product key={product.id} item={product} />
          ))}
        </div>
        <div className="row mt-5">
          <div className="col-md-12 text-center">
            <div className="site-block-27">
              <ul>
                <li>
                  <a href="index.html">&lt;</a>
                </li>
                <li className="active">
                  <span>1</span>
                </li>
                <li>
                  <a href="index.html">2</a>
                </li>
                <li>
                  <a href="index.html">&gt;</a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Store;
