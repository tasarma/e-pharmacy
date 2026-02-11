export interface ProductType {
  id: number;
  name: string;
  image: string;
  price: string;
  sale_price?: string;
  is_on_sale?: boolean;
  expire_date: string;
  contents: string;
}

export interface OrderItemType {
  productId: string | undefined;
  qty: number;
}

export interface UserOrderItemsType {
  productId: string | undefined;
  qty: number;
  product: ProductType;
  price: number;
}

export interface ProductProps {
  item: ProductType;
}

export interface OrderItemProps {
  item: OrderItemType;
}

export interface ProductSpecification {
  key: string;
  value: string;
}

export interface ProductOrderingInformation {
  material: string;
  description: string;
  packaging: string;
}

export enum HttpMethods {
  GET = "GET",
  POST = "POST",
  PUT = "PUT",
  DELETE = "DELETE",
  PATCH = "PATCH",
}

export interface TokenType {
  access: string;
  refresh: string;
}