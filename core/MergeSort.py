class MergeSorter:
    def sort(self, items, key=None):
        """Ordenar usando Merge Sort"""
        if not items:
            return []
        
        if len(items) <= 1:
            return items
        
        mid = len(items) // 2
        left = self.sort(items[:mid], key)
        right = self.sort(items[mid:], key)
        
        return self._merge(left, right, key)
    
    def _merge(self, left, right, key):
        """Fusión de dos listas ordenadas"""
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            left_val = key(left[i]) if key else left[i]
            right_val = key(right[j]) if key else right[j]
            
            if left_val <= right_val:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result