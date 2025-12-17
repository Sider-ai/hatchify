import clsx, { type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * enhancer tw class
 */
/*#__NO_SIDE_EFFECTS__*/
export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));
