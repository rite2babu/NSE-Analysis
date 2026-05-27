# OrderHub Custom Field Extension Guide

## Overview
OrderHub uses Angular-based extensibility framework for adding custom fields to order forms.

## Extension Approaches

### 1. Extension Configuration (Recommended)
OrderHub supports declarative extensions via JSON configuration.

**Location**: `extensions/order-extensions.json`

```json
{
  "orderForm": {
    "customFields": [
      {
        "id": "customField1",
        "label": "Custom Reference",
        "type": "text",
        "section": "orderDetails",
        "position": "after:orderNumber",
        "required": false,
        "maxLength": 50,
        "validation": {
          "pattern": "^[A-Z0-9-]+$",
          "message": "Only uppercase letters, numbers and hyphens allowed"
        }
      },
      {
        "id": "priorityLevel",
        "label": "Priority Level",
        "type": "dropdown",
        "section": "orderDetails",
        "position": "after:customField1",
        "required": true,
        "options": [
          { "value": "LOW", "label": "Low" },
          { "value": "MEDIUM", "label": "Medium" },
          { "value": "HIGH", "label": "High" },
          { "value": "URGENT", "label": "Urgent" }
        ]
      },
      {
        "id": "deliveryInstructions",
        "label": "Special Delivery Instructions",
        "type": "textarea",
        "section": "shipping",
        "position": "end",
        "required": false,
        "maxLength": 500,
        "rows": 4
      },
      {
        "id": "giftWrap",
        "label": "Gift Wrap Required",
        "type": "checkbox",
        "section": "orderDetails",
        "position": "end",
        "defaultValue": false
      },
      {
        "id": "requestedDeliveryDate",
        "label": "Requested Delivery Date",
        "type": "date",
        "section": "shipping",
        "position": "after:shippingMethod",
        "required": false,
        "validation": {
          "minDate": "today",
          "maxDate": "+90days"
        }
      }
    ]
  }
}
```

### 2. Angular Component Extension

**Create Custom Field Component**

`src/app/extensions/custom-order-fields/custom-order-fields.component.ts`

```typescript
import { Component, Input, OnInit } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { OrderExtensionService } from '@orderhub/core';

@Component({
  selector: 'app-custom-order-fields',
  templateUrl: './custom-order-fields.component.html',
  styleUrls: ['./custom-order-fields.component.scss']
})
export class CustomOrderFieldsComponent implements OnInit {
  @Input() orderForm: FormGroup;
  @Input() mode: 'create' | 'edit' | 'view';
  
  priorityLevels = [
    { value: 'LOW', label: 'Low' },
    { value: 'MEDIUM', label: 'Medium' },
    { value: 'HIGH', label: 'High' },
    { value: 'URGENT', label: 'Urgent' }
  ];

  constructor(private extensionService: OrderExtensionService) {}

  ngOnInit(): void {
    this.initializeCustomFields();
  }

  private initializeCustomFields(): void {
    // Add custom form controls
    this.orderForm.addControl('customReference', this.fb.control('', [
      Validators.pattern(/^[A-Z0-9-]+$/),
      Validators.maxLength(50)
    ]));
    
    this.orderForm.addControl('priorityLevel', this.fb.control('MEDIUM', [
      Validators.required
    ]));
    
    this.orderForm.addControl('deliveryInstructions', this.fb.control('', [
      Validators.maxLength(500)
    ]));
    
    this.orderForm.addControl('giftWrap', this.fb.control(false));
    
    this.orderForm.addControl('requestedDeliveryDate', this.fb.control(null));
  }

  onPriorityChange(value: string): void {
    // Custom logic when priority changes
    if (value === 'URGENT') {
      this.orderForm.get('requestedDeliveryDate')?.setValidators([Validators.required]);
    } else {
      this.orderForm.get('requestedDeliveryDate')?.clearValidators();
    }
    this.orderForm.get('requestedDeliveryDate')?.updateValueAndValidity();
  }
}
```

**Template**

`src/app/extensions/custom-order-fields/custom-order-fields.component.html`

```html
<div class="custom-fields-section" [formGroup]="orderForm">
  <!-- Custom Reference -->
  <div class="form-field">
    <label for="customReference">Custom Reference</label>
    <input 
      id="customReference"
      type="text"
      formControlName="customReference"
      placeholder="Enter custom reference"
      [readonly]="mode === 'view'"
    />
    <div class="error" *ngIf="orderForm.get('customReference')?.invalid && orderForm.get('customReference')?.touched">
      Only uppercase letters, numbers and hyphens allowed
    </div>
  </div>

  <!-- Priority Level -->
  <div class="form-field">
    <label for="priorityLevel">Priority Level *</label>
    <select 
      id="priorityLevel"
      formControlName="priorityLevel"
      (change)="onPriorityChange($event.target.value)"
      [disabled]="mode === 'view'"
    >
      <option *ngFor="let level of priorityLevels" [value]="level.value">
        {{ level.label }}
      </option>
    </select>
  </div>

  <!-- Requested Delivery Date -->
  <div class="form-field">
    <label for="requestedDeliveryDate">
      Requested Delivery Date
      <span *ngIf="orderForm.get('priorityLevel')?.value === 'URGENT'">*</span>
    </label>
    <input 
      id="requestedDeliveryDate"
      type="date"
      formControlName="requestedDeliveryDate"
      [min]="today"
      [readonly]="mode === 'view'"
    />
  </div>

  <!-- Gift Wrap -->
  <div class="form-field checkbox-field">
    <input 
      id="giftWrap"
      type="checkbox"
      formControlName="giftWrap"
      [disabled]="mode === 'view'"
    />
    <label for="giftWrap">Gift Wrap Required</label>
  </div>

  <!-- Delivery Instructions -->
  <div class="form-field">
    <label for="deliveryInstructions">Special Delivery Instructions</label>
    <textarea 
      id="deliveryInstructions"
      formControlName="deliveryInstructions"
      rows="4"
      maxlength="500"
      placeholder="Enter any special delivery instructions"
      [readonly]="mode === 'view'"
    ></textarea>
    <div class="char-count">
      {{ orderForm.get('deliveryInstructions')?.value?.length || 0 }}/500
    </div>
  </div>
</div>
```

### 3. Register Extension Module

`src/app/extensions/extensions.module.ts`

```typescript
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { OrderHubExtensionModule } from '@orderhub/extensions';
import { CustomOrderFieldsComponent } from './custom-order-fields/custom-order-fields.component';

@NgModule({
  declarations: [
    CustomOrderFieldsComponent
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    OrderHubExtensionModule
  ],
  exports: [
    CustomOrderFieldsComponent
  ]
})
export class ExtensionsModule {
  constructor() {
    // Register extension points
    OrderHubExtensionModule.registerExtension({
      id: 'custom-order-fields',
      type: 'order-form',
      component: CustomOrderFieldsComponent,
      position: 'after:orderDetails'
    });
  }
}
```

### 4. Backend API Extension

**Extend Order Model**

`src/models/order-extension.model.ts`

```typescript
export interface OrderExtension {
  customReference?: string;
  priorityLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  deliveryInstructions?: string;
  giftWrap: boolean;
  requestedDeliveryDate?: Date;
}

export interface ExtendedOrder extends Order {
  extensions: OrderExtension;
}
```

**API Service**

`src/services/order-extension.service.ts`

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ExtendedOrder } from '../models/order-extension.model';

@Injectable({
  providedIn: 'root'
})
export class OrderExtensionService {
  private apiUrl = '/api/orders';

  constructor(private http: HttpClient) {}

  saveOrderWithExtensions(order: ExtendedOrder): Observable<ExtendedOrder> {
    return this.http.post<ExtendedOrder>(`${this.apiUrl}`, order);
  }

  updateOrderExtensions(orderId: string, extensions: OrderExtension): Observable<void> {
    return this.http.patch<void>(`${this.apiUrl}/${orderId}/extensions`, extensions);
  }

  getOrderWithExtensions(orderId: string): Observable<ExtendedOrder> {
    return this.http.get<ExtendedOrder>(`${this.apiUrl}/${orderId}`);
  }
}
```

### 5. Database Schema Extension

**Sterling OMS Extn Tables Pattern**

```sql
-- Custom order extensions table
CREATE TABLE YFS_ORDER_EXTN (
    ORDER_HEADER_KEY VARCHAR(24) NOT NULL,
    CUSTOM_REFERENCE VARCHAR(50),
    PRIORITY_LEVEL VARCHAR(10) NOT NULL DEFAULT 'MEDIUM',
    DELIVERY_INSTRUCTIONS VARCHAR(500),
    GIFT_WRAP CHAR(1) DEFAULT 'N',
    REQUESTED_DELIVERY_DATE TIMESTAMP,
    CREATETS TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    MODIFYTS TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ORDER_HEADER_KEY),
    FOREIGN KEY (ORDER_HEADER_KEY) REFERENCES YFS_ORDER_HEADER(ORDER_HEADER_KEY)
);

CREATE INDEX IDX_ORDER_EXTN_PRIORITY ON YFS_ORDER_EXTN(PRIORITY_LEVEL);
CREATE INDEX IDX_ORDER_EXTN_REF ON YFS_ORDER_EXTN(CUSTOM_REFERENCE);
```

## Migration Checklist

- [ ] Identify all custom fields from Sterling JSP pages
- [ ] Create extension configuration JSON
- [ ] Develop Angular components for complex fields
- [ ] Extend backend API models
- [ ] Update database schema
- [ ] Implement validation rules
- [ ] Add field-level security/permissions
- [ ] Create unit tests for custom components
- [ ] Update API documentation
- [ ] Migrate existing data from Sterling to OrderHub schema

## Field Type Mapping

| Sterling JSP | OrderHub Angular | Notes |
|--------------|------------------|-------|
| `<input type="text">` | `type: "text"` | Standard text input |
| `<select>` | `type: "dropdown"` | Dropdown with options |
| `<textarea>` | `type: "textarea"` | Multi-line text |
| `<input type="checkbox">` | `type: "checkbox"` | Boolean field |
| `<input type="date">` | `type: "date"` | Date picker |
| Custom JSP tag | Angular component | Requires custom component |

## Best Practices

1. **Use declarative config** for simple fields (text, dropdown, checkbox)
2. **Create components** for complex logic or custom UI
3. **Validate on both** client and server side
4. **Maintain backward compatibility** during migration
5. **Document all extensions** for future maintenance
6. **Use TypeScript interfaces** for type safety
7. **Follow OrderHub naming conventions** for consistency
8. **Test with existing Sterling data** before go-live

## Common Patterns

### Conditional Field Display
```typescript
showField(fieldName: string): boolean {
  const orderType = this.orderForm.get('orderType')?.value;
  return fieldName === 'giftWrap' ? orderType === 'RETAIL' : true;
}
```

### Dynamic Validation
```typescript
updateValidation(fieldName: string, required: boolean): void {
  const control = this.orderForm.get(fieldName);
  if (required) {
    control?.setValidators([Validators.required]);
  } else {
    control?.clearValidators();
  }
  control?.updateValueAndValidity();
}
```

### Field Dependencies
```typescript
setupFieldDependencies(): void {
  this.orderForm.get('priorityLevel')?.valueChanges.subscribe(priority => {
    if (priority === 'URGENT') {
      this.updateValidation('requestedDeliveryDate', true);
    }
  });
}