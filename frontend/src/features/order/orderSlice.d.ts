import { OrderItemType } from "../../types";
interface OrderItemsState {
    loading: boolean;
    orderInfo: any;
    error: string | null;
    success: boolean;
}
export declare const createOrderItems: import("@reduxjs/toolkit").AsyncThunk<unknown, OrderItemType, import("@reduxjs/toolkit").AsyncThunkConfig>;
declare const _default: import("redux").Reducer<OrderItemsState>;
export default _default;
