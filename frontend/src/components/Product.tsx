import { Link } from "react-router-dom";
import { ProductProps } from "../types";

function Product({ item }: ProductProps) {
  return (
    <div className="col-sm-6 col-lg-4 text-center item mb-4 item-v2">
      {item.is_on_sale && <span className="onsale">İNDİRİM</span>}
      <Link to={`/product/${item.id}`} state={{ product: item }}>
        <img src={item.image} alt={item.name} />
        <h3 className="text-dark">{item.name}</h3>
        <p className="price">
          {item.sale_price ? (
            <>
              ₺ <del>{item.price}</del> &mdash; ₺{item.sale_price}
            </>
          ) : (
            <>₺{item.price}</>
          )}
        </p>
      </Link>
    </div>
  );
}

export default Product;
