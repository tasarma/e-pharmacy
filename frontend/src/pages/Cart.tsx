import { OrderItemType, UserOrderItemsType } from "../types";
import { useGetUserOrderItemsQuery } from "../utils/ApiService";

function Cart() {
  const { data: orders } = useGetUserOrderItemsQuery();
  function direct(): void {
    throw new Error("Function not implemented.");
  }

  return (
    <div className="site-section">
      <div className="container">
        <div className="row mb-5">
        {orders?.map((order: UserOrderItemsType) => (
                 <form className="col-md-12" method="post">
                 <div className="site-blocks-table">
                   <table className="table table-bordered">
                     <thead>
                       <tr>
                         <th className="product-thumbnail">Image</th>
                         <th className="product-name">Product</th>
                         <th className="product-price">Price</th>
                         <th className="product-quantity">Quantity</th>
                         <th className="product-total">Total</th>
                         <th className="product-remove">Remove</th>
                       </tr>
                     </thead>
                     <tbody>
                       <tr>
                         <td className="product-thumbnail">
                           <img src={order.product.image} alt="Image" className="img-fluid"/>
                         </td>
                         <td className="product-name">
                           <h2 className="h5 text-black">{order.product.name}</h2>
                         </td>
                         <td>{order.product.sale_price}</td>
                         <td>
                           <div className="input-group mb-3" style={{maxWidth: "120px"}}>
                             <div className="input-group-prepend">
                               <button className="btn btn-outline-primary js-btn-minus" type="button">-</button>
                             </div>
                             <input type="text" className="form-control text-center" value={order.qty} placeholder=""
                               aria-label="Example text with button addon" aria-describedby="button-addon1"></input>
                             <div className="input-group-append">
                               <button className="btn btn-outline-primary js-btn-plus" type="button">+</button>
                             </div>
                           </div>
         
                         </td>
                         <td>{order.price}</td>
                         <td><a href="#" className="btn btn-primary height-auto btn-sm">X</a></td>
                       </tr>
                     </tbody>
                   </table>
                 </div>
               </form>
          ))}
    
        </div>
      </div>
    </div>
  );
};

export default Cart;
