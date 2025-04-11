import { Badge } from "@/components/ui/ui-components";

const getStatusBadge = (status) => {
    switch (status) {
    case 'completed':
        return <Badge variant="success">Completed</Badge>;
    case 'in_progress':
        return <Badge variant="primary">In Progress</Badge>;
    case 'pending':
        return <Badge variant="warning">Pending</Badge>;
    // case 'delayed':
    //   return <Badge variant="danger">已延期</Badge>;
    default:
        return <Badge>Unknown</Badge>;
    }
};
export default getStatusBadge;

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('zh-CN');
  };
export { formatDate };
