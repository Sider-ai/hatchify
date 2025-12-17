export type ApiExtraResponse<T = undefined> = T;

export type ApiResponse<T = undefined> = {
	message: string;
	code: number;
	data: T;
};

export type WithPagination<T = undefined> = {
	page: number;
	limit: number;
	total: number;
	pages: number;
	hasNext: boolean;
	hasPrev: boolean;
	list: T[];
};
