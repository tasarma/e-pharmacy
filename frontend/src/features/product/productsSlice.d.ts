import { ProductType } from "../../types";
interface ProductsState {
    items: ProductType[];
    loading: boolean;
    error: string | null;
}
export declare const fetchProducts: import("@reduxjs/toolkit").AsyncThunk<ProductType[], void, import("@reduxjs/toolkit").AsyncThunkConfig>;
declare const _default: import("redux").Reducer<ProductsState>;
export default _default;
