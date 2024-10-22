import { TItem, TItemList } from "./models";

function Item({
  date,
  exchange_product_id,
   exchange_product_name,
  delivery_basis_name,
total, count, volume}: TItem) {
  const ind = exchange_product_name.indexOf(' ', 25)
  return (
    <tr >     
      <td >{date}</td> 
      <td >{exchange_product_id}</td>
      <td>{exchange_product_name.slice(0, ind)}</td>
      <td>{delivery_basis_name}</td>
      <td >{count}</td>
      <td >{volume}</td>
      <td >{total}</td> 
    </tr>)
}

export default function ListView({items}: TItemList) {
  return (
    <div className="table-responsive display-block width-100">
    <table className="table table-striped table-condensed ">
    <thead>
      <tr className="success">
        <th scope='row'>Дата торгов</th>
        <th scope='row'>ID</th>
        <th scope='row'>Наименование</th>
        <th scope='row'>База</th>
        <th scope='row'>Количество договоров</th>
        <th scope='row'>Цена договора</th>
        <th scope='row'>Итоговая стоимость</th>
      </tr>
    </thead>
    <tbody>
      {items.map((item: TItem) =>
        <Item key={item.exchange_product_id} {...item} />)}  
    </tbody>    
    </table>
    </div>
  )
}