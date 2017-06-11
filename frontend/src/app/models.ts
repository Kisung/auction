export class Auction {
  constructor(
    public id: number,
    public title: string,
    public description: string,
  ) {}
}

export class Bid {
    constructor(
        public auction_id: number,
        public name: string,
        public email: string,
        public price: number,
    ) {}
}