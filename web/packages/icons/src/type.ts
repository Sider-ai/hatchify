import { RefAttributes, SVGProps } from 'react';

export type SVGAttributes = Partial<SVGProps<SVGSVGElement>>;
type ElementAttributes = RefAttributes<SVGSVGElement> & SVGAttributes;

export interface IconProps extends ElementAttributes {
  size?: string | number;
}
