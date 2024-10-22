import { useState, useEffect } from 'react';
import ListView from './ListView.tsx';
import { TItem } from './models.tsx';

import Dates from './Dates.tsx';
import axios from 'axios';


export default function Store () {
  const [source, setSource] = useState<string>('http://localhost:8000/api/get_trading_results/')
  const [items, setItems] = useState<TItem[]>([])
  const handler = (url: string) => {    
    setSource(url)
    fetchItems(url)
  }
  
  const fetchItems = (url) => {
    axios.get(url)
      .then(res => {setItems(res.data)})
      }
      
  useEffect(()=>{
    fetchItems(source)}, [])

  return (
    <div>
      <h1>Trading Results</h1>
      <ListView items={items} />
      <Dates handleSource={handler}/>
    </div>
  )
    
}
