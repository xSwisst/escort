import searchIcon from '@/assets/icons/search.svg';
import { MaskedIcon } from '@/shared/ui/MaskedIcon';

type SearchIconProps = {
  size?: number;
  className?: string;
};

export function SearchIcon({ size = 16, className }: SearchIconProps) {
  return <MaskedIcon src={searchIcon} size={size} className={className ? `search-icon ${className}` : 'search-icon'} />;
}
